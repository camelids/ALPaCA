from bs4 import BeautifulSoup
from file_utils import *

class Page:
    
    def __init__(self, page):
        """Instantiate a Page object, given the file name
        of an HTML page.
        
        Parameters
        ----------
        page : string
            File name of HTML page.
        """
        self.fname = page
        self.basedir = dir_name(page)
        relpath = file_name(page)
        self.html = self.new_object(relpath, 'html')
        with open(page) as f:
            self.objects = self.parse_objects(f.read())

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
        
        fullpath = os.path.join(self.basedir, path)
        size = file_size(fullpath)
        if not ftype:
            ftype = file_extension(path)
        
        return {'path': path,
                'fullpath': fullpath,
                'size': size,
                'type': ftype,
                'delay': delay}
