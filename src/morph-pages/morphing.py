"""Morphing objects.

Functions of this script can be used to morph objects
of web pages (e.g.: text, images).
"""
import os
import page
import numpy as np
from file_utils import *
from morph_utils import create_object, morph_html, morph_object

def morph_page_distribution(fname, page_sampler, outdir):
    """Morph original page to look as it comes from the
    specified distribution.

    Parameters
    ----------
    fname : str
        File name of the HTML file of the original page.
    page_sampler : sampling.PageSampler
        Page sampler.
    outdir : str
        Destination directory.
    """
    original = page.Page(fname)
    html_size = original.html['size']
    sizes = original.get_sizes()
    number = len(sizes)                 # Number of objects.

    if not sizes:
        min_objs = 0
    else:
        min_objs = min(sizes)

    target_html_size, target_sizes = page_sampler.sample_page(min_count = number,
                                                              min_html = html_size,
                                                              min_objs = min_objs)
                                                            
    # Try to morph. If it doesn't work (some sizes where too
    # small), notify and try again.
    try:
        morph_page(original, target_html_size, target_sizes, outdir)
    except NotImplementedError as e:
        raise e
    except:
        print "Couldn't morph {} with {}".format(sizes, target_sizes)
        morph_page_distribution(fname, page_sampler, outdir)

def morph_page_target(fname, target_html_size, target_sizes, outdir):
    """Morph original page to look like a target, and put
    the morphed content in outdir directory.
    
    Parameters
    ----------
    fname : string
        File name of the HTML file of the original page.
    target_html_size : int
        Size of the HTML file of the target page.
    target_sizes : list of int
        Sizes of the objects of the target page.
    outdir : string
        Output directory.
    """
    original = page.Page(fname)
    morph_page(original, target_html_size, target_sizes, outdir)

def _next_multiple(x, m):
    """Returns k*m, where k is the smallest int for which x <= m*k.
    """
    assert m > 0
    k = 1
    while k*m < x:
        k += 1

    return k*m

def morph_page_deterministic(fname, S, L, max_S, outdir):
    """Morph original page to contain a multiple of L objects,
    each of them with size multiple of S.
    Parameters
    ----------
    fname : string
        File name of the HTML file of the original page.
    S : int
        Size parameter.
    L : int
        Length (number of objects) parameters.
    outdir : string
        Output directory.
    max_S : int
        Must be a multiple of S.
        If new objects are created, their sizes are sampled
        uniformly in [S, 2S, ..., max_S].
    """
    if max_S % S != 0:
        raise Exception('max_S should be a multiple of S.')
    original = page.Page(fname)
    original_html_size = original.html['size']
    original_sizes = original.get_sizes()
    original_number = len(original_sizes)
    # Pad total length to next multiple of L.
    target_number = _next_multiple(original_number, L)
    # Pad the size of each object to the next multiple
    # of S.
    target_html_size = _next_multiple(original_html_size, S)
    target_sizes = []
    for s in original_sizes:
        t = _next_multiple(s, S)
        target_sizes.append(t)
    # Create remaining objects.
    sizes = range(0, max_S+1, S)            # Possible size for new objects.
    del sizes[0]                            # Remove size 0.
    for i in range(target_number - len(target_sizes)):
        s = np.random.choice(sizes)
        target_sizes.append(s)

    try:
        morph_page(original, target_html_size, target_sizes, outdir)
    except:
        # This can happen if original_html_size and target_html_size are
        # close. This means that when adding stuff to the mophed html page
        # (e.g., image references) the page may become bigger than target_html_size,
        # which makes morphing fail.
        print "Couldn't morph {} with {}".format(original_html_size, target_html_size)
        target_html_size += S
        morph_page(original, target_html_size, target_sizes, outdir)

def morph_page(original, target_html_size, target_sizes, outdir):
    """Morph original page to look like a target, and put
    the morphed content in outdir directory.
    
    Parameters
    ----------
    original : Page instance
        Original page to morph.
    target_html_size : int
        Size of the HTML file of the target page.
    target_sizes : list of int
        Sizes of the objects of the target page.
    outdir : string
        Output directory.
    """
    # Which object should be morphed with what.
    original_sizes = original.get_sizes()
    pairs, remainders = match_sizes(original_sizes, target_sizes)

    # Morph objects.
    original_objects = original.objects
    for i, size in pairs:
        src = original_objects[i]['fullpath']
        src_relative = original_objects[i]['path']
        print 'Morphing {} to size {}.'.format(src_relative, size)
        dst = os.path.join(outdir, src_relative)
        make_path(dst)
        #print 'Full: {}, relative: {}'.format(src, src_relative)
        morph_object(src, dst, size)

    # Add padding objects.
    add_to_html = ''
    for i, size in enumerate(remainders):
        dst = os.path.join(outdir, 'random-objects', 'rnd-{}.png'.format(i))
        dst_relative = os.path.join('random-objects', 'rnd-{}.png'.format(i))
        print 'Adding {} with size {}.'.format(dst, size)
        make_path(dst)
        create_object(dst, size)
        add_to_html += '<img src="{}" style="visibility:hidden">'.format(dst_relative)

    # Morph HTML page.
    if original.html['size'] + len(add_to_html) > target_html_size:
        raise Exception('The size of the original page is larger than the target one.')
    with open(original.fname) as f:
        original_html = f.read()
    # Put add_to_html (links to padding images) right before the end of
    # <body>.
    body = original_html.find('</body>')
    if body == -1:
        raise Exception('Am I really looking at an HTML file?')
    tmp = original_html[:body] + add_to_html + original_html[body:]
    new_html = morph_html(tmp, target_html_size)
    dst = os.path.join(outdir, file_name(original.fname))
    print 'Morphing {} to size {}.'.format(dst, target_html_size)
    make_path(dst)
    with open(dst, 'w') as f:
        f.write(new_html)

def match_sizes(original_sizes, target_sizes):
    """Decide which original size should be paded with which
    target size.

    Parameters
    ----------
    original_sizes : list of int
        Sizes of original objects.
    target_sizes : list of int
        Sizes of target objects.
    """
    # Get indexes of sorted original_sizes, and sort target_sizes.
    oi = sorted(range(len(original_sizes)), key=lambda x: original_sizes[x])
    ts = sorted(target_sizes)

    pairs = []
    remainders = [x for x in target_sizes]

    for i in oi:
        for j in range(len(ts)):
            size = ts[j]
            if original_sizes[i] <= size:
               pairs.append((i, size))
               remainders.remove(size)
               # Remove previous j sizes
               ts = ts[j+1:]
               break
        else:
            raise Exception('Original page > Target page.')

    return pairs, remainders
