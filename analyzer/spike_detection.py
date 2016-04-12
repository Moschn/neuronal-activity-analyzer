""" Base class for a spike detection algorithm """


class Spike_detection(object):
    """ Base class for a spike detection algorithm. Implementations must
    overwrite all methods """

    def __init__(self):
        """ Constructor """
        raise NotImplemented

    def detect_spikes(self, dataset):
        """ Overwritten in implementation

        @dataset: numpy array [roi][time] containing activity of all the rois

        @returns: numpy array [roi][time] containing time of the spikes
        detected"""
