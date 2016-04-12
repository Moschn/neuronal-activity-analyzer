""" Wavelet Detection Method (WDM) from 
"Spike Detection Using the Continuous Wavelet Transform"
Authors: Nenadic, Zoran and Burdick, Joel W"""
from analyzer.spike_detection import Spike_detection
from math import floor, ceil, log, sqrt, exp, pi
import numpy
from skimage.feature import peak_local_max

class WDM(Spike_detection):

    def __init__(self, min_spike_width, max_spike_width):
        """ Constructor 
        @min_spike_width minimum spike width in data points
        @max_spike_width maximum spike width in data points"""
        self.min_spike_width = min_spike_width
        self.max_spike_width = max_spike_width

    def detect_spikes(self, dataset):
        wavelet_transform = self._wavelet_transform(dataset,
                                                    self.wavelet_difference_of_gauss)

        # remove noise
        wavelet_transform_threshold = self._wavelet_remove_noise(
            wavelet_transform)
        
        maxima = numpy.zeros(len(dataset))
        for i in range(0, len(wavelet_transform_threshold)):
            wavelet_row = wavelet_transform_threshold[i]
            local_maxima = self._find_local_maxima1D(wavelet_row, 1)
            maxima = numpy.add(maxima, local_maxima)
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
            for j in range(max(0, i-size//2), min(len(dataset)-size, i+size//2)):
                if cur_cluster > numpy.sum(input_abs[j:j+size]):
                    bigger_cluster = True

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

    def _wavelet_remove_noise(self, wavelet_transform):
        wavelet_transform_threshold = numpy.copy(wavelet_transform)
        for i in range(0, len(wavelet_transform)):
            # estimate variance
            # according to the papaer this is accurate
            avg_wavelet_transform = numpy.average(wavelet_transform[i])
            variance = numpy.median(wavelet_transform[i]-avg_wavelet_transform)
            threshold = variance/0.6745*sqrt(2*log(len(wavelet_transform[i])))

            # hard threshold the values below this threshold
            lowindices = wavelet_transform[i] < threshold
            wavelet_transform_threshold[i][lowindices] = 0

        return wavelet_transform_threshold

    def _wavelet_transform(self, dataset, gen_wavelet):
        wt = numpy.zeros((self.max_spike_width - self.min_spike_width,
                          len(dataset)))
        for j in range(self.min_spike_width, self.max_spike_width):
            wavelet = gen_wavelet(j)
            wt[j-self.min_spike_width] = numpy.convolve(dataset, wavelet, 'same')
        return wt

    def wavelet_difference_of_gauss(self, number_of_points):
        """ This function returns a wavelet created by a difference of two gauss
        functions"""
        sigma1 = 0.1
        sigma2 = 0.4
        wavelet = numpy.zeros((number_of_points))
        sq2pi = sqrt(2*numpy.pi)
        for i in range(0, number_of_points):
            x = i / number_of_points - 0.5
            print(x)
            g1 = 1 / (sq2pi * sigma1) * exp(-0.5*x*x/(sigma1*sigma1))
            print(g1)
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
