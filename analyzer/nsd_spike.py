""" N times standard deviation spike detection method """
from analyzer.spike_detection import Spike_detection
import numpy
from math import floor


class SD_spike_detection(Spike_detection):

    def __init__(self, n):
        self.n = n

    def detect_spikes(self, dataset):
        # correct the bleaching
        # avg of first 10% and last 10% is used to estimate the slope

        start_avg = numpy.mean(dataset[0:len(dataset)//20])
        end_avg = numpy.mean(dataset[19*len(dataset)//20:20*len(dataset)//20])
        slope = start_avg - end_avg

        # correct signal
        dataset_corrected = numpy.zeros(len(dataset))
        for idx, data in enumerate(dataset):
            corr_factor = floor(slope * (len(dataset)-idx)/len(dataset))
            dataset_corrected[idx] = dataset[idx] - corr_factor

        threshold = (numpy.mean(dataset_corrected) +
                     numpy.std(dataset_corrected)*self.n)
        dataset_thresh = dataset_corrected > threshold
        i = 0
        spikes = []
        while i < len(dataset):
            if dataset_thresh[i]:
                j = i + 1
                while j < len(dataset) and dataset_thresh[j]:
                    j += 1
                spikes.append(i+numpy.argmax(dataset_corrected[i:j]))
                i = j + 1
            else:
                i += 1

        # from matplotlib import pyplot
        # pyplot.figure()
        # pyplot.subplot(211)
        # pyplot.plot(dataset)
        # pyplot.subplot(212)
        # pyplot.plot(dataset_corrected)
        # pyplot.hlines([threshold, numpy.mean(dataset_corrected)], 0, 1000)
        # pyplot.show()

        return spikes
