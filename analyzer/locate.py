""" Base class for a localisation algorithm """


class locate(object):
    """ Base class for an algorithm, that locates neurons in a frame.
    Implementations must overwrite"""
    def __init__(self):
        """ Constructor. Possible initialization of the implementation
        is calculated here."""

        raise NotImplemented

    def analyze_frame(cls, frame):
        """ Analyze new frame
        @param frame: Numpy array of a new frame

        @returns: numpy array that maps each pixel to a neuron. 0 correspons
                  to no neuron.
        """

        raise NotImplemented
