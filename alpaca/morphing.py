"""Morphing objects.

Functions of this script can be used to morph objects
of web pages (e.g.: text, images).
"""
import os
import page
import numpy as np
from file_utils import *
from morph_utils import create_object, morph_html, morph_object

MAX_FAILS = 20    # How many times we should sample a target page from a
                  # distribution and fail, before raising an error


class InvalidTarget(Exception):
    """Raised when the original page cannot be morphed to the provided
    target.
    """
    pass


def morph_page_distribution(html, page_sampler):
    """Morph an html page to look as it comes from the
    specified distribution.

    Parameters
    ----------
    html : str
        Original HTML page.
    page_sampler : sampling.PageSampler
        Page sampler.
    """
    original = page.Page(html)
    html_size = len(original.content)
    sizes = original.get_sizes()
    number = len(sizes)                 # Number of objects.

    if not sizes:
        min_objs = 0
    else:
        min_objs = min(sizes)

    # NOTE: one could preemptively sample from the distribution,
    # and modify morph_page_distribution() to accept such sampled data

    # Try to morph. If it doesn't succeed (some sizes where too
    # small), notify and try again.
    # Does not report failure for MAX_FAILS tries
    morphed = None
    fail_count = 0
    while fail_count < MAX_FAILS:
        target = page_sampler.sample_page(min_count = number, 
                                          min_html = html_size,
                                          min_objs = min_objs)
        try:
            morphed = morph_page(original, *target)
            break
        except InvalidTarget:
            # TODO: verbose logging
            print("Couldn't morph {} with {}".format((html_size, sizes),
                                                     *target))
            fail_count += 1

    # If too many failures in morphing
    if morphed is None:
        raise InvalidTarget('Original page > Target page. Try changing distributions')

    return morphed

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
        print("Couldn't morph {} with {}".format(original_html_size,
                                                 target_html_size))
        target_html_size += S
        morph_page(original, target_html_size, target_sizes, outdir)

def morph_page(original, target_html_size, target_sizes):
    """Morph original page to look like a target (html and object sizes),
    and returns the morphed content as a string.
    
    Parameters
    ----------
    original : Page instance
        Original page to morph.
    target_html_size : int
        Size of the HTML file of the target page.
    target_sizes : list of int
        Sizes of the objects of the target page.
    """
    # Which object should be morphed with what.
    original_sizes = original.get_sizes()
    pairs, remainders = match_sizes(original_sizes, target_sizes)

    new_html = original.content

    # Morph objects.
    original_objects = original.objects
    for i, size in pairs:
        obj_path = original_objects[i]['path']
        obj_type = original_objects[i]['type']
        new_path = '{}?type={}&size={}'.format(obj_path, obj_type, size)
        new_html = new_html.replace(obj_path, new_path)

    # Add padding objects.
    add_to_html = []
    for i, size in enumerate(remainders):
        new_obj = '<img src="/rnd/{}" style="visibility:hidden">'.format(size)
        add_to_html.append(new_obj)
    add_to_html = ''.join(add_to_html)

    # Morph HTML page.
    if len(new_html) + len(add_to_html) > target_html_size:
            raise InvalidTarget('Original page > Target page.')

    # Put add_to_html (links to padding images) right before the end of
    # <body>.
    body = new_html.find('</body>')
    if body == -1:
        raise Exception('Am I really looking at an HTML file?')
    new_html = new_html[:body] + add_to_html + new_html[body:]
    new_html = morph_html(new_html, target_html_size)

    return new_html

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
            raise InvalidTarget('Original page > Target page.')

    return pairs, remainders
