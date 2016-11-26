import pickle
import numpy as np

class PageSampler(object):
    """Samples size and number of objects in a page.
    """

    def __init__(self, random_state=0):
        # We DO NOT want to initialise the random state in experiments.
        #np.random.seed(random_state)
        pass

    def sample_page(self):
        """Samples a page's parameters.

        Returns
        -------
        html_size : int
            Size of HTML page.
        objs_size : list of int.
            Size of each object.
        """
        pass

class KDEIndividual(PageSampler):

    def __init__(self, file_count, file_html, file_objs, random_state=0):
        super(self.__class__, self).__init__(random_state)

        self.count_kde = self.read_kde(file_count)
        self.html_kde = self.read_kde(file_html)
        self.objs_kde = self.read_kde(file_objs)

    def sample_page(self, min_count=0, min_html=0, min_objs=0):
        """Samples html_size and size of objects objs_size.
        
        Parameters
        ----------
        min_count : int
            Minimum number of objects.
        min_html : int
            Minimum size of HTML page.
        min_objs : int
            Minimum size of an object.

        Returns
        -------
        html_size : int
            Size of HTML.
        objs_size : list of int
            Size of each object.
        """
        # Count.
        count = int(self.count_kde.sample(1)[0][0])
        while count < min_count:
            count = int(self.count_kde.sample(1)[0][0])
        # HTML
        html_size = int(self.html_kde.sample(1)[0][0])
        while html_size < min_html:
            html_size = int(self.html_kde.sample(1)[0][0])
        # Objects.
        objs_size = []
        for i in range(count):
            o = int(self.objs_kde.sample(1)[0][0])
            while o < min_objs:
                o = int(self.objs_kde.sample(1)[0][0])
            objs_size.append(o)

        return html_size, objs_size

    def read_kde(self, fname):
        with open(fname, 'rb') as f:
            return pickle.load(f)

class KDEMultivariate(PageSampler):

    def __init__(self, kde_file, random_state=0):
        super(self.__class__, self).__init__(random_state)
        self.kde = self.read_kde(kde_file)

    def sample_page(self, min_count=0, min_html=0, min_objs=0):
        """Samples html_size and size of objects objs_size.
        
        Parameters
        ----------
        min_count : int
            Minimum number of objects.
        min_html : int
            Minimum size of HTML page.
        min_objs : int
            Minimum size of an object.

        Returns
        -------
        html_size : int
            Size of HTML.
        objs_size : list of int
            Size of each object.
        """
        page = self.kde.sample(1)[0]
        page = page[page > min(min_html, min_objs)]
        while len(page) < min_count:
            page = self.kde.sample(1)[0]
            page = page[page > min(min_html, min_objs)]

        page = page.astype(int)
        html_size = page[0]
        objs_size = list(page[1:])

        return html_size, objs_size

    def read_kde(self, fname):
        with open(fname, 'rb') as f:
            return pickle.load(f)


class Histogram(PageSampler):

    def __init__(self, file_count, file_html, file_objs, random_state=0):
        super(self.__class__, self).__init__(random_state)

        self.count_hist = self.read_distribution(file_count)
        self.html_hist = self.read_distribution(file_html)
        self.objs_hist = self.read_distribution(file_objs)
        
    def sample_page(self, min_count=None, min_html=None, min_objs=None):
        """Samples html_size and size of objects objs_size.
        
        Parameters
        ----------
        min_count : int
            Minimum number of objects.
        min_html : int
            Minimum size of HTML page.
        min_objs : int
            Minimum size of an object.

        Returns
        -------
        html_size : int
            Size of HTML.
        objs_size : list of int
            Size of each object.
        """
        # Count.
        if min_count:
            count_hist = self.remove_smaller_than(self.count_hist[0],
                                                  self.count_hist[1],
                                                  min_count)
        else:
            count_hist = self.count_hist
        count = self.sample_distribution(*count_hist)
        # HTML.
        if min_html:
            html_hist = self.remove_smaller_than(self.html_hist[0],
                                                 self.html_hist[1],
                                                 min_html)
        else:
            html_hist = self.html_hist
        html_s = self.sample_distribution(*html_hist)
        # Objects.
        if min_objs:
            objs_hist = self.remove_smaller_than(self.objs_hist[0],
                                                 self.objs_hist[1],
                                                 min_objs)
        else:
            objs_hist = self.objs_hist
        objs_s = self.sample_distribution(size=count, *objs_hist)
    
        return html_s, objs_s

    def read_distribution(self, fname):
        """Read a histogram distribution file ".his".
    
        An histogram distribution file .his has the following format.
        Each row indicates a quantity s_i and its respective
        occurrence probability p_i. The quantities s_i and p_i
        are separated by a space.
        Values are assumed to be integers.
    
        Parameters
        ----------
        fname : str
            Name of the .his file.
    
        Return
        ------
        values : list of int
            List of possible values.
        probabilities : list of float
            Probabilities associated with the values.
            sum(probabilities) = 1.0.
        """
        with open(fname, 'r') as f:
            entries = f.read().strip().split('\n')
    
        values = []
        probabilities = []
        for e in entries:
            v, p = e.split(' ')
            values.append(int(v))
            probabilities.append(float(p))
    
        if not np.isclose(sum(probabilities), 1.0):
            raise Exception("Corrupted distribution file: probabilities do not " +
                            "sum up to 1.")
        
        return values, probabilities
    
    def sample_distribution(self, values, probabilities, size=1, min_val=None):
        """Sample from histogram with replacement.
    
        The histogram is specified by a list of values, and the
        respective probabilities.
        Size represents the sample size.
        Returns an array of values.
    
        Parameters
        ----------
        values : list
            List of the values that can be taken.
        probabilities : list of float
            Occurrence probabilities of each value.
        size : int (Default: 1)
            Sample size.
        min_val : int (Default: None)
            If specified, the sampled value is at least min_val.
    
        Return
        ------
        value : array of values
            Array of values of size size.
        """
        if len(values) != len(probabilities):
            raise Exception('The size of values must be equal to the size of probabilities.')
        
        return np.random.choice(values, size=size, replace=True, p=probabilities)
    
    def remove_smaller_than(self, values, probabilities, value):
        """Removes from an histogram all the values smaller than value.
    
        Normalises the resulting histogram, and returns it.
    
        Parameters
        ----------
        values : list
            List of the values that can be taken.
        probabilities : list of float
            Occurrence probabilities of each value.
        value : int
            Smallest value allowed.
        
        Return
        ------
        values : list of int
            List of possible values.
        probabilities : list of float
            Probabilities associated with the values.
            sum(probabilities) = 1.0.
        """
        new_v = []
        new_p = []
        for i, v in enumerate(values):
            if v >= value:
                new_v.append(v)
                new_p.append(probabilities[i])
        
        new_p = np.array(new_p) / sum(new_p)
    
        return new_v, list(new_p)
