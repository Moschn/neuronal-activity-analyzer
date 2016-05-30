""" Wavelet Detection Method (WDM) from
"Spike Detection Using the Continuous Wavelet Transform"
Authors: Nenadic, Zoran and Burdick, Joel W"""
from .spike_detection import Spike_detection
from math import log, sqrt
import numpy
from scipy.signal import ricker


class WDM(Spike_detection):

    def __init__(self, config, exposure_time):
        """ Constructor
        @min_spike_width minimum spike width in data points
        @max_spike_width maximum spike width in data points"""
        self.min_spike_width = int(5*config['min_spike_width']/exposure_time)
        self.max_spike_width = int(5*config['max_spike_width']/exposure_time)
        self.step_size = (self.max_spike_width - self.min_spike_width) // 100
        self.steps = 100

    def detect_spikes(self, dataset):
        self.min_spike_width = min(self.min_spike_width, len(dataset))
        self.max_spike_width = min(self.max_spike_width, len(dataset))
        if self.min_spike_width == self.max_spike_width:
            raise Exception("Video has not enough frames")

        dataset = dataset-numpy.mean(dataset)
        wt = self._wavelet_transform(dataset, self.wavelet_ricker)

        # remove noise
        (wt_thresh, noise_prob) = self._wavelet_remove_noise(wt)

        time = self._find_spikes(wt_thresh, dataset, noise_prob)

        maxima_time = []
        # filter out false positives
        i = 0
        while i < len(time):
            curr_max = time[i]
            close_maxima = [curr_max]
            j = i+1
            while j < len(time):
                next_max = time[j]
                if next_max < time[j-1]+self.min_spike_width:
                    close_maxima.append(next_max)
                else:
                    break
                j += 1
            # get maximum in dataset for these close peaks
            biggest = -1000
            selected_max = curr_max
            for m in close_maxima:
                if dataset[m] > biggest:
                    biggest = dataset[m]
                    selected_max = m
            maxima_time.append(selected_max)
            i = j

        return numpy.array(maxima_time)

    def _find_spikes(self, wavelet_transform, dataset, noise_probability):
        """ This function implements the statistical methods described in the 
        paper to determine if a correlation with the wavelet is really a spike
        or just noise"""
        maxima = numpy.zeros(len(dataset))
        for i in range(0, len(wavelet_transform)):
            wavelet_row = wavelet_transform[i]
            mean = numpy.mean(numpy.fabs(wavelet_row))
            var = numpy.median(numpy.fabs(wavelet_row-mean))/0.6745
            l = 0
            l_m = 36.7368
            gamma = noise_probability[i]

            # catch a few possible Math domain errors
            if mean != 0 and gamma != 0:
                threshold = mean/2 + var**2 / mean * (l * l_m + log(gamma))
            else:
                threshold = 100000000

            # all correlations above the threshold are spikes
            highindices = (wavelet_transform[i]) > threshold

            maxima[highindices] = 1

        # now there are regions were spikes are
        # In order to get only one exact time for each spike the maximum of
        # the signal in the possible range is taken
        peaks_time = []
        i = 0
        while i < len(dataset):
            if maxima[i] == 1:
                j = i
                curr_max = -1
                max_ind = i
                while j < len(dataset) and maxima[j] == 1:
                    if dataset[j] > curr_max:
                        curr_max = dataset[j]
                        max_ind = j
                    j += 1
                peaks_time.append(max_ind)
                i = j+1
            else:
                i += 1

        return peaks_time

    def _wavelet_remove_noise(self, wavelet_transform):
        wavelet_transform_threshold = numpy.copy(wavelet_transform)
        noise_probability = []
        for i in range(0, len(wavelet_transform)):
            wavelet_row = wavelet_transform[i]
            # estimate variance
            # according to the paper this is accurate
            avg = numpy.mean(wavelet_row)
            variance = numpy.median(numpy.fabs(wavelet_row - avg))/0.6745
            threshold = variance*sqrt(2*log(len(wavelet_row)))

            # hard threshold the values below this threshold
            lowind = numpy.fabs(wavelet_row) < threshold

            wavelet_transform_threshold[i][lowind] = 0

            # append probability to threshold_probability
            # used in probabilistic test for spikes
            nr_noise = numpy.sum(lowind)
            if len(wavelet_row) - nr_noise != 0:
                probability = (nr_noise / (len(wavelet_row) - nr_noise))
            else:
                probability = 99999999

            noise_probability.append(probability)

        return wavelet_transform_threshold, noise_probability

    def _wavelet_transform(self, dataset, gen_wavelet):
        wt = numpy.zeros((self.steps, len(dataset)))
        for j in range(0, self.steps):
            width = self.min_spike_width + j*self.step_size
            wavelet = gen_wavelet(width)
            conv = numpy.correlate(dataset, wavelet, 'same')
            wt[j] = conv
        return wt

    def wavelet_ricker(self, number_of_points):
        a = self.min_spike_width/2 * number_of_points/self.max_spike_width
        return ricker(number_of_points, a)
