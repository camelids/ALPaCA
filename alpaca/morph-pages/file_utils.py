import os
from shutil import copyfile
from PIL import PngImagePlugin

def file_size(fname):
    """Returns the size in byte of a file.

    Wrapper around os.stat call.
    """
    return os.stat(fname).st_size

def copy_file(src, dst):
    """Copy file src into dst.
    
    Wrapper around shutil copyfile.
    """
    copyfile(src, dst)

def dir_name(path):
    """Directory name.

    Wrapper around os dirname.
    """
    return os.path.dirname(path)

def file_name(path):
    """Return the file name.

    Wrapper around os basename.
    """
    return os.path.basename(path)

def make_path(path):
    """Creates the required directories to
    make the path accessible.
    
    make_path('a/b/c/test.txt') will create (if missing) the
    directories a/b/c/.
    """
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass
    except Exception as e:
        raise e

def remove_file(fname):
    """Removes the file from the system.
    
    Wrapper around os remove file.
    """
    return os.remove(fname)

def file_extension(fname):
    """Returns the extension of a file name.

    Wrapper around os function.
    """
    _, ext = os.path.splitext(fname)

    return ext[1:]

# wrapper around PIL 1.1.6 Image.save to preserve PNG metadata
# public domain, Nick Galbreath
# http://blog.modp.com/2007/08/python-pil-and-png-metadata-take-2.html
def save_png(im, fout):
    """Stores a PNG images keeping `info'.
    """
    # they are not user-added metadata
    reserved = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')
    # undocumented class
    meta = PngImagePlugin.PngInfo()
    # copy metadata into new object
    for k,v in im.info.iteritems():
        if k in reserved:
            continue
        meta.add_text(k, v, 0)

    im.save(fout, "PNG", pnginfo=meta)


class FilePaddingError(Exception):
    

    def __init__(self, message):
        MSG = "The size of the file '{}' is larger than the padding target size.".format(message)
        super(Exception, self).__init__(MSG)

