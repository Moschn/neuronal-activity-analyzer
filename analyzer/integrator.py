""" Base class for a integration/sum of the pixels """


class Integrator(object):
    """ Base class for an algorithm that sums or integrates (or anything does
    anything else) the brightness of the regions of interest (ROIs) """

    def __init__(self, roi):
        """ Contructor. An array representing the various ROIs is needed.
        The array contains a number at every ROI. The number represents the
        unique nmumber of the respective ROI """

        raise NotImplemented

    def process_frame(self, frame):
        """ Process new frame
        @param frame: Numpy array of the new frame

        @returns: list of all ROIs with a respective activity measure. """

        raise NotImplemented
