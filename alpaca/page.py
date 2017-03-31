from os.path import abspath, realpath

from bs4 import BeautifulSoup

from file_utils import *

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
        # Images
        links = soup.find_all('img', src=True)
        objects = []
        for img in links:
            path = img['src']
            obj = self.new_object(path)
            objects.append(obj)
        # CSS
        links = soup.find_all('link', rel='stylesheet')
        for css in links:
            path = css['href']
            obj = self.new_object(path)
            objects.append(obj)

        return objects

    def new_object(self, path, ftype=None, delay=0):
        fullpath = abspath(realpath('.' + path))
        size = file_size(fullpath)
        if not ftype:
            ftype = file_extension(fullpath)
        
        return {'path': path,
                'fullpath': fullpath,
                'size': size,
                'type': ftype,
                'delay': delay}
