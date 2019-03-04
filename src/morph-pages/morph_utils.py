"""Morphing objects.

Functions of this script can be used to morph objects
of web pages (e.g.: text, images).
"""
import os
import page
import random
import string
from PIL import Image
from file_utils import *

def morph_html(html, target_size):
    """Morphs html text.

    Accepts html text pads it to a target_size.
    Returns the padded text.

    Parameters
    ----------
    html : str
        HTML text to morph.
    target_size : int
        Size (in bytes) that the text should have.
    """
    return __pad_html(html, target_size)

def morph_object(fname, dst, target_size):
    """Morphs an object.

    Accepts an object and pads it to a target_size.
    Stores the new object into dst.

    Parameters
    ----------
    fname : str
    target_size : int
        Size (in bytes) that the image should have.
    """
    ext = file_extension(fname)
    if ext == 'png':
        morph = __pad_jpeg
    elif ext == 'jpg':
        morph = __pad_jpeg
    elif ext == 'bmp':
        morph = __pad_bmp
    elif ext == 'gif':
        morph = __pad_gif
    elif ext == 'tiff':
        morph = __pad_tiff
    elif ext == 'pdf':
        morph = __pad_pdf
    elif ext == 'css':
        morph = __pad_css
    elif ext == 'svg':
        morph = __pad_svg
    else:
        raise NotImplementedError('Morphing files with extension {}'.format(ext))
    
    morph(fname, dst, target_size)

def create_object(fname, size):
    """Creates a binary file with random data.
    
    The file can be given any extension.

    Parameters
    ----------
    fname : str
        Name of the file.
    size : int
        Size in bytes of the file.
    """
    if size <= 0:
        raise FilePaddingError('New file')
    with open(fname, 'wb') as f:
        rnd = random_bytes(size)
        f.write(rnd)

def random_chars(n):
    """Returns a string of random characters in [a-zA-Z0-9].
    """
    chars = string.ascii_letters + string.digits

    return ''.join([random.choice(chars) for i in range(n)])

def random_bytes(n):
    """Return a string of n random bytes suitable for cryptographic use.

    This function returns random bytes from an OS-specific randomness source.
    This is a wrapper around os.urandom() function.
    """
    return os.urandom(n)

def __pad_html(html, target_size):
    """Pads html text.

    Adds a comment to the provided html text containing random
    data, so that the corresponding page reaches the target size.
    
    Parameters
    ----------
    fname : string
        HTML text.
    target_size : int
        Size (in bytes) that the text should have.
    """
    size = len(html)
    if size == target_size:
        return html
    # Padding size
    comment_start = '<!--'
    comment_end = '-->'
    pad = target_size - size - len(comment_start) - len(comment_end)
    if pad < 0:
        raise FilePaddingError('HTML file')
    # Pad
    rnd = random_chars(pad)
    html += '{}{}{}'.format(comment_start, rnd, comment_end)

    return html

def __split_html(html, target_size):
    """Reduce the size of the html text, returns
    the reduced one, and a new one.
    """
    raise NotImplementedError('Splitting HTML files.')

def __pad_css(fname, dst, target_size):
    """Pads a CSS file.
    
    Adds a comment at the end of the CSS file, and
    stores the result in a new file.
    
    Parameters
    ----------
    fname : string
        CSS file name.
    dst : string
        Name of the destination file.
    target : int
        Size (in bytes) that the file should have.
    """
    size = file_size(fname)
    if size == target_size:
        copy_file(fname, dst)
        return
    # Padding size
    comment_start = '/*'
    comment_end = '*/'
    pad = target_size - size - len(comment_start) - len(comment_end)
    if pad < 0:
        raise FilePaddingError(fname)
    with open(fname) as f:
        text = f.read()
    # Pad
    rnd = random_chars(pad) 
    text += '{}{}{}'.format(comment_start, rnd, comment_end)
    with open(dst, 'w') as f:
        f.write(text)

def __pad_png(fname, dst, target_size):
    """Pad a PNG image.

    Adds random content to the comment section
    of a PNG image so that it gets the required
    target size.
    
    Parameters
    ----------
    fname : str
        Name of the image file.
    dst : str
        Name of the destination file.
    target_size : int
        Desired size.
    """
    if file_size(fname) == target_size:
        copy_file(fname, dst)
        return
    # Store tmp image, get its size.
    # We do this to know the size of the image
    # when compressed using PIL library. Another option is to
    # force PIL to use the same compression method which was
    # used in the original image.
    img = Image.open(fname)
    tmpfname = fname + '-tmp.png'
    # We want 'Comment' section to appear in the
    # file. Otherwise, we'll have discrepancies in the
    # size we obtain at the end.
    if not 'Comment' in img.info:
        img.info['Comment'] = ''
    save_png(img, tmpfname)
    pad = target_size - file_size(tmpfname)
    remove_file(tmpfname)
    if pad < 0:
        raise FilePaddingError(fname)
    img = Image.open(fname)
    rnd = random_bytes(pad)
    if not 'Comment' in img.info:
        img.info['Comment'] = ''
    img.info['Comment'] += rnd
    save_png(img, dst)

def __pad_jpeg(fname, dst, target_size):
    """Pad a jpeg image.

    Adds random data to a jpeg image so that it
    takes the required target size.
    
    Parameters
    ----------
    fname : str
        Name of the image file.
    dst : str
        Name of the destination file.
    target_size : int
        Desired size.
    """
    with open(fname, 'rb') as f:
        img = f.read()
    pad = target_size - len(img)
    if pad < 0:
        raise FilePaddingError(fname)
    rnd = random_bytes(pad)
    img += rnd
    with open(dst, 'wb') as f:
        f.write(img)

def __pad_bmp(img, dst, target_size):
    """Pad a BMP image.

    Adds random data to a jpeg image so that it
    takes the required target size.
    
    Parameters
    ----------
    fname : str
        Name of the image file.
    dst : str
        Name of the destination file.
    target_size : int
        Desired size.
    """
    # Same procedure as JPEG.
    __pad_jpeg(img, dst, target_size)

def __pad_gif(img, dst, target_size):
    """Pad a GIF image.
    
    Parameters
    ----------
    fname : str
        Name of the image file.
    dst : str
        Name of the destination file.
    target_size : int
        Desired size.
    """
    # Same procedure as JPEG.
    __pad_jpeg(img, dst, target_size)

def __pad_tiff(img, dst, target_size):
    """Pad a TIFF image.
    
    Parameters
    ----------
    fname : str
        Name of the image file.
    dst : str
        Name of the destination file.
    target_size : int
        Desired size.
    """
    raise NotImplementedError('Morphing TIFF files')

def __pad_pdf(img, dst, target_size):
    """Pad a PDF file.
    
    Parameters
    ----------
    fname : str
        Name of the image file.
    dst : str
        Name of the destination file.
    target_size : int
        Desired size.
    """
    raise NotImplementedError('Morphing PDF files')
    
def __pad_svg(fname, dst, target_size):
    """Pad a SVG file.
    
    Adds a (XML) comment at the end of the SVG file, and
    stores the result in a new file.
    
    Parameters
    ----------
    fname : str
        Name of the SVG file
    dst : str
        Name of the destination file.
    target : int
        Size (in bytes) that the file should have.
    """
   
    with open(fname, 'rb') as f:
        text = f.read()
        text = __pad_html(text, target_size)
    
    with open(dst, 'wb') as f:
        f.write(text)
