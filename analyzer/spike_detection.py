""" Base class for a spike detection algorithm """

from .settings import THREAD_COUNT

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

    def detect_spikes_parallel(self, activities):
        try:  # python 3.5
            from concurrent.futures import ThreadPoolExecutor
            spikes = []
            with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
                futures = [executor.submit(self.detect_spikes, activity)
                           for activity in activities]
            for future in futures:
                maxima_time = future.result()
                spikes.append(maxima_time)
            return spikes
        except ImportError:
            spikes = []
            for activity in activities:
                maxima_time = self.detect_spikes(activity)
                spikes.append(maxima_time)
            return spikes
