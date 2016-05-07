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

    def detect_spikes_parallel(self, activities):
        try:  # python 3.5
            from concurrent.futures import ThreadPoolExecutor
            act = activities.T
            spikes = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.detect_spikes, activity)
                           for activity in act]
                for future in futures:
                    maxima_time = future.result()
                    spikes.append(maxima_time)
            return spikes
        except ImportError:
            act = activities.T
            spikes = []
            for activity in act:
                maxima_time = self.detect_spikes(activity)
                spikes.append(maxima_time)
            return spikes
