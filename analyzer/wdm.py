""" Wavelet Detection Method (WDM) from
"Spike Detection Using the Continuous Wavelet Transform"
Authors: Nenadic, Zoran and Burdick, Joel W"""
from analyzer.spike_detection import Spike_detection
from math import floor, ceil, log, sqrt, exp
import numpy
from scipy.signal import argrelextrema


class WDM(Spike_detection):

    def __init__(self, min_spike_width, max_spike_width):
        """ Constructor
        @min_spike_width minimum spike width in data points
        @max_spike_width maximum spike width in data points"""
        self.min_spike_width = min_spike_width
        self.max_spike_width = max_spike_width

    def detect_spikes(self, dataset):
        wavelet_transform = self._wavelet_transform(dataset,
                                                    self.wavelet_diff_of_gauss)

        # remove noise
        wavelet_transform_threshold = self._wavelet_remove_noise(
            wavelet_transform)

        # maxima = self._find_spikes(wavelet_transform_threshold)

        maxima = numpy.zeros(len(dataset))
        for i in range(0, len(wavelet_transform_threshold)):
            wavelet_row = wavelet_transform_threshold[i]
            #local_maxima = self._find_local_maxima1D(wavelet_row, 1)
            local_maxima_fast = self._local_maxima_fast(wavelet_row)
            #from matplotlib import pyplot
            #pyplot.figure()
            #pyplot.subplot(311)
            #pyplot.plot(wavelet_row)
            #pyplot.subplot(312)
            #pyplot.plot(local_maxima)
            #pyplot.subplot(313)
            #pyplot.plot(local_maxima_fast)
            #pyplot.show()
            maxima = numpy.add(maxima, local_maxima_fast)

        # threshold mean/2
        # mean = numpy.mean(maxima)
        # lowindices = maxima < mean
        # maxima[lowindices] = 0

        time = []
        i = 0
        while i < len(maxima)-1:
            j = i
            while maxima[j] <= 0 and j < len(maxima)-1:
                j += 1
            while maxima[j] > 0 and j < len(maxima)-1:
                j += 1
            if j != len(maxima)-1:
                time.append(numpy.argmax(maxima[i:j]) + i)
            i = j

        return (maxima, time)

    def _find_spikes(self, wavelet_transform):
        maxima = numpy.zeros(len(wavelet_transform[0]))
        for i in range(0, len(wavelet_transform)):
            avg = numpy.mean(wavelet_transform[i])
            var = numpy.median(numpy.fabs(wavelet_transform[i]-avg))/0.6745
            mean = numpy.mean(wavelet_transform[i])
            l = 0.188
            l_m = 36.7368
            gamma = self.noise_probability[i]

            if gamma == 0:
                gamma = 1/len(wavelet_transform[i])

            if mean != 0:
                threshold = mean/2 + var**2 / mean * (l * l_m + log(gamma))
            else:
                threshold = mean/2

            maxima = numpy.add(maxima, wavelet_transform[i] > threshold)

        return maxima

    def _find_local_maxima1D(self, dataset, size):
        """ This function finds local maxima in a 1D array. The size is
        specified in datapoints. I think this only works for size=1"""
        # input_abs = numpy.absolute(dataset)
        input_abs = dataset
        maxima = numpy.zeros(len(dataset))
        for i in range(0, len(input_abs)-size):
            cur_cluster = numpy.sum(input_abs[i:i+size])
            bigger_cluster = False
            # for j in range(max(0, i-size//2), min(len(dataset)-size, i+size//2)):
            #    if cur_cluster > numpy.sum(input_abs[j:j+size]):
            #        bigger_cluster = True

            if bigger_cluster is False:
                if i < size:
                    left_bigger = True
                else:
                    left_bigger = cur_cluster > numpy.sum(input_abs[i-size:i-1])
                if i > len(input_abs)-2*size:
                    right_bigger = True
                else:
                    right_bigger = cur_cluster > numpy.sum(
                        input_abs[i+size+1:i+2*size+1])

                if left_bigger and right_bigger:
                    maxima[i] = 1
        return maxima

    def _local_maxima_fast(self, dataset):
        maxima = numpy.zeros(len(dataset))
        maxima[argrelextrema(dataset, numpy.greater)] = 1
        return maxima

    

    def _wavelet_remove_noise(self, wavelet_transform):
        wavelet_transform_threshold = numpy.copy(wavelet_transform)
        self.noise_probability = []
        for i in range(0, len(wavelet_transform)):
            wavelet_row = wavelet_transform[i][self.min_spike_width+i:
                                               (len(wavelet_transform[i]) -
                                                self.min_spike_width-i)]
            # estimate variance
            # according to the paper this is accurate
            avg = numpy.mean(wavelet_row)
            variance = numpy.median(numpy.fabs(wavelet_row - avg))
            threshold = variance/0.6745*sqrt(2*log(len(wavelet_row)))

            # hard threshold the values below this threshold
            lowindices = wavelet_transform_threshold[i] < threshold
            wavelet_transform_threshold[i][lowindices] = 0

            # append probability to threshold_probability
            # used in probabilistic test for spikes
            probability = numpy.sum(lowindices)/(len(wavelet_transform[i]) -
                                                 numpy.sum(lowindices)+1)
            print("{}: nr of cut values: {}, percent: {}".format(threshold,
                                                                 numpy.sum(lowindices),
                                                                 probability))
            self.noise_probability.append(probability)

        return wavelet_transform_threshold

    def _wavelet_transform(self, dataset, gen_wavelet):
        wt = numpy.zeros((self.max_spike_width - self.min_spike_width,
                          len(dataset)))
        for j in range(self.min_spike_width, self.max_spike_width):
            wavelet = gen_wavelet(j)
            conv = numpy.convolve(dataset, wavelet, 'valid')
            wt[j-self.min_spike_width] = numpy.lib.pad(conv, ((j-1)//2, (j)//2), 'constant', constant_values=0)
        return wt

    def wavelet_diff_of_gauss(self, number_of_points):
        """ This function returns a wavelet created by a difference of two gauss
        functions"""
        sigma1 = 0.1
        sigma2 = 0.4
        wavelet = numpy.zeros((number_of_points))
        sq2pi = sqrt(2*numpy.pi)
        for i in range(0, number_of_points):
            x = i / number_of_points - 0.5
            g1 = 1 / (sq2pi * sigma1) * exp(-0.5*x*x/(sigma1*sigma1))
            g2 = 1 / (sq2pi * sigma2) * exp(-0.5*x*x/(sigma2*sigma2))
            wavelet[i] = g1 - g2
        energy = numpy.dot(wavelet, wavelet)
        return wavelet / sqrt(energy)

    def wavelet_sym6(self, number_of_points):
        """ This function returns a sym6 wavelet with number_of_points """
        skeleton_sym6 = [0.015404109327027373,
                         0.0034907120842174702,
                         -0.11799011114819057,
                         -0.048311742585633,
                         0.4910559419267466,
                         0.787641141030194,
                         0.3379294217276218,
                         -0.07263752278646252,
                         -0.021060292512300564,
                         0.04472490177066578,
                         0.0017677118642428036,
                         -0.007800708325034148]
        return self._scale_wavelet(number_of_points, skeleton_sym6)

    def wavelet_bior1_5(self, number_of_points):
        skeleton_bior1_5 = [0.01657281518405971,
                            -0.01657281518405971,
                            -0.12153397801643787,
                            0.12153397801643787,
                            0.7071067811865476,
                            0.7071067811865476,
                            0.12153397801643787,
                            -0.12153397801643787,
                            -0.01657281518405971,
                            0.01657281518405971]
        return self._scale_wavelet(number_of_points, skeleton_bior1_5)


    def _scale_wavelet(self, number_of_points, skeleton):
        wavelet = []
        scaling_factor = 1/sqrt(number_of_points)
        for i in range(0, number_of_points):
            pos = i / (number_of_points-1) * (len(skeleton)-1)
            interpol = pos - floor(pos)
            datapoint = (skeleton[floor(pos)] + interpol *
                         (skeleton[ceil(pos)] - skeleton[floor(pos)]) *
                         scaling_factor)
            wavelet.append(datapoint)
        return wavelet
