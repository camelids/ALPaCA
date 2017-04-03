import os
from os.path import abspath, realpath, splitext

from bs4 import BeautifulSoup

class Page:
    
    def __init__(self, html_string):
        """Instantiate a Page object, given the contents of an HTML
        page as a string.
        
        Parameters
        ----------
        html_string : string
            The content of an HTML page.
        """
        self.content = html_string
        self.objects = self.parse_objects(html_string)

    def get_sizes(self):
        """Return the size of the objects.
        
        """
        return [x['size'] for x in self.objects]

    def parse_objects(self, html):
        """Return the path to the objects of an html page.

        Parameters
        ----------
        html : string
            HTML page.
        """
        soup = BeautifulSoup(html, 'html.parser')
        objects = []
        # img tags
        links = soup.find_all('img', src=True)
        for img in links:
            path = img['src']
            obj = self.new_object(path)
            objects.append(obj)
        # link tags
        links = soup.find_all('link', href=True)
        for link in links:
            # CSS and images
            # :class:`bs4.element.Tag` re-implements :meth:`__getattr__` in an unusal way.
            # The "attributes" we want are actually key/val pairs stored in a dict under the
            # instance attribute `attrs`. :meth:`get` is a convenience method which passes
            # it's arguments through to :meth:`self.attrs.get`.
            if (link.get('rel', '')[0] == 'stylesheet'
                or link.get('type', '').startswith('image/'))
                path = link['href']
                obj = self.new_object(path)
                objects.append(obj)
        # script tags
        links = soup.find_all('script', src=True)
        for script in links:
            path = script['src']
            obj = self.new_object(path)
            objects.append(obj)
        
        return objects

    def new_object(self, path, ftype=None, delay=0):
        fullpath = abspath(realpath('.' + path.split('?')[0]))
        size = os.stat(fullpath).st_size
        if not ftype:
            ftype = splitext(fullpath)[1][1:]
        
        return {'path': path,
                'fullpath': fullpath,
                'size': size,
                'type': ftype,
                'delay': delay}
