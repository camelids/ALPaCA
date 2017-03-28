from os.path import abspath, dirname, join

ABS_FILE_DIR_NAME=abspath(dirname(__file__))

counts = join(ABS_FILE_DIR_NAME, 'counts.kde')
html = join(ABS_FILE_DIR_NAME, 'html.kde')
objects = join(ABS_FILE_DIR_NAME, 'objects.kde')
