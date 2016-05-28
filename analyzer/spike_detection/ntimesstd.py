
""" N times standard deviation spike detection method """
from .spike_detection import Spike_detection
import numpy


class NTimesSTD(Spike_detection):

    def __init__(self, config, exposure_time):
        if 'nSD_n' in config:
            n = config['nSD_n']
        else:
            print("""If the n*SD spike detection method is
            selected an additional 'nSD_n' parameter is required""")
            print("A n value of 1 is assumed")
            n = 1
        self.n = float(n)

    def detect_spikes(self, dataset):
        threshold = numpy.std(dataset)*self.n
        dataset_thresh = dataset > threshold
        i = 0
        spikes = []
        while i < len(dataset):
            if dataset_thresh[i]:
                j = i + 1
                while j < len(dataset) and dataset_thresh[j]:
                    j += 1
                spikes.append(i+numpy.argmax(dataset[i:j]))
                i = j + 1
            else:
                i += 1

        return numpy.array(spikes)
