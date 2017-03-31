"""Morphing objects.

Functions of this script can be used to morph objects
of web pages (e.g.: text, images).
"""
import os
import random
import string

import page
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

def morph_object(content, ftype, target_size):
    """Pads the content of an object to the specified size.

    Parameters
    ----------
    content : str
        Object content.
    ftype : str
        The object extension (e.g., 'png', 'jpg', ...).
    target_size : int
        Size (in bytes) that the object should have.
    """
    ftype = ftype.lower()
    switch = {'png': __pad_binary,
              'jpg': __pad_binary,
              'jpeg': __pad_binary,
              'gif': __pad_binary,
              'bmp': __pad_binary,
              'css': __pad_css,
              'js': __pad_css,
              'default': __pad_binary
             }
    
    if ftype in switch:
        morph = switch[ftype]
    else:
        print("Morphing file with type '{}' (this may not work)".format(ftype))
        morph = switch['default']
    
    return morph(content, target_size)

def create_object(size):
    """Creates a binary object with random data.
    
    The file can be given any extension.

    Parameters
    ----------
    size : int
        Size in bytes of the object.
    """
    if size <= 0:
        raise FilePaddingError('New file')
    
    return random_bytes(size)

def random_chars(n):
    """Returns a string of random characters in [a-zA-Z0-9].
    """
    chars = string.ascii_letters + string.digits

    return ''.join([random.choice(chars) for i in range(n)])

def random_bytes(n):
    """Return a string of n random bytes. This is not suitable for
    cryptographic use, but preserves the /dev/urandom entropy pool which
    we rely on for actually important cryptographic operations. Our goal
    is to avoid our padding being compressed, for which
    non-cryptographic randomness is sufficient.
    """
    return str(bytearray(random.getrandbits(8) for _ in xrange(n)))

def __pad_html(html, target_size):
    """Pads html text.

    Adds a comment to the html page containing random
    data, so that the page reaches the target size.
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

def __pad_css(content, target_size):
    """Pads a CSS file content.
    
    Adds a comment at the end of the CSS.
    
    Parameters
    ----------
    content : string
        CSS file content
    target_size : int
        Size (in bytes) that the file should have.
    """
    size = len(content)
    if size == target_size:
        return content

    # Determine padding size
    comment_start = '/*'
    comment_end = '*/'
    pad = target_size - size - len(comment_start) - len(comment_end)
    if pad < 0:
        raise FilePaddingError('CSS file')

    # Pad
    rnd = random_chars(pad) 
    morphed = '{}{}{}{}'.format(content, comment_start, rnd, comment_end)

    return morphed


def __pad_binary(content, target_size):
    """Pad the (binary) content of an object to target size.

    Parameters
    ----------
    content : str
        Object content.
    target_size : int
        Target size in bytes.
    """
    if len(content) > target_size:
        raise FilePaddingError("target_size too small")

    return content + random_bytes(target_size - len(content))
