""" Wavelet Detection Method (WDM) from
"Spike Detection Using the Continuous Wavelet Transform"
Authors: Nenadic, Zoran and Burdick, Joel W"""
from analyzer.spike_detection import Spike_detection
from math import floor, ceil, log, sqrt, exp
import numpy
from scipy.signal import ricker


class WDM(Spike_detection):

    def __init__(self, min_spike_width, max_spike_width):
        """ Constructor
        @min_spike_width minimum spike width in data points
        @max_spike_width maximum spike width in data points"""
        self.min_spike_width = min_spike_width
        self.max_spike_width = max_spike_width

    def detect_spikes(self, dataset):
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

        # cut off first and last peak if too close to edge
        if len(maxima_time) > 0:
            if maxima_time[0] < self.min_spike_width//2:
                del maxima_time[0]
            if maxima_time[-1] > len(dataset) - self.min_spike_width//2:
                del maxima_time[-1]

        return numpy.array(maxima_time)

    def _find_spikes(self, wavelet_transform, dataset, noise_probability):
        maxima = numpy.zeros(len(wavelet_transform[0]))
        for i in range(0, len(wavelet_transform)):
            wavelet_row = wavelet_transform[i][(self.min_spike_width+i)//2:
                                               (len(wavelet_transform[i]) -
                                                (self.min_spike_width+i)//2)]
            mean = numpy.mean(numpy.fabs(wavelet_row))
            var = numpy.median(numpy.fabs(wavelet_row-mean))/0.6745
            l = 0
            l_m = 36.7368
            gamma = noise_probability[i]

            if mean != 0:
                threshold = mean/2 + var**2 / mean * (l * l_m + log(gamma))
            else:
                threshold = 100000000

            highindices = (wavelet_transform[i]) > threshold
            highindices[0:(self.min_spike_width+i)//2] = False
            highindices[len(wavelet_transform[i])-(self.min_spike_width+i)//2:
                        len(highindices)] = False

            # from matplotlib import pyplot
            # if i % 25 == 0:
            #     pyplot.figure()
            #     pyplot.subplot(211)
            #     pyplot.plot(wavelet_transform[i])
            #     print(i)
            #     print("mean: {}".format(mean))
            #     print("var: {}".format(var))
            #     print("log(noise/signal): {}".format(log(gamma)))
            #     print("treshold: {}".format(threshold))
            #     pyplot.subplot(212)
            #     pyplot.plot(highindices)
            #     pyplot.show()

            maxima[highindices] = 1

        peaks_time = []
        i = 0
        while i < len(dataset):
            if maxima[i] == 1:
                j = i
                curr_max = -1
                max_ind = i
                while maxima[j] == 1:
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
            wavelet_row = wavelet_transform[i][(self.min_spike_width+i)//2:
                                               (len(wavelet_transform[i]) -
                                                (self.min_spike_width+i)//2)]
            # estimate variance
            # according to the paper this is accurate
            avg = numpy.mean(wavelet_row)
            variance = numpy.median(numpy.fabs(wavelet_row - avg))/0.6745
            threshold = variance*sqrt(2*log(len(wavelet_row)))

            length_diff = len(wavelet_transform[i]) - len(wavelet_row)
            len2 = length_diff//2
            # hard threshold the values below this threshold
            lowind_unpad = numpy.fabs(wavelet_row) < threshold
            len3 = len(wavelet_transform[i]) - (len2 + len(lowind_unpad))
            lowindices = numpy.lib.pad(lowind_unpad, (len2, len3),
                                       'constant', constant_values=False)
            wavelet_transform_threshold[i][lowindices] = 0

            # append probability to threshold_probability
            # used in probabilistic test for spikes
            nr_noise = numpy.sum(lowind_unpad)
            if len(wavelet_row) - nr_noise != 0:
                probability = (nr_noise / (len(wavelet_row) - nr_noise))
            else:
                probability = 99999999
            # print("{}: {}/{}, percent: {}".format(threshold,
            #                                       nr_noise,
            #                                       len(wavelet_row),
            #                                       probability))
            noise_probability.append(probability)

        return wavelet_transform_threshold, noise_probability

    def _wavelet_transform(self, dataset, gen_wavelet):
        wt = numpy.zeros((self.max_spike_width - self.min_spike_width,
                          len(dataset)))
        for j in range(self.min_spike_width, self.max_spike_width):
            wavelet = gen_wavelet(j)
            conv = numpy.convolve(dataset, wavelet, 'valid')
            wt[j-self.min_spike_width] = numpy.lib.pad(conv,
                                                       ((j-1)//2, (j)//2),
                                                       'constant',
                                                       constant_values=0)
        return wt

    def wavelet_ricker(self, number_of_points):
        a = self.min_spike_width/2 * number_of_points/self.max_spike_width
        wavelet = ricker(number_of_points, a)
        if numpy.sum(wavelet) > 1:
            print("dafuq: energy: {}".format(sum(wavelet)))
        return wavelet

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
        energy = numpy.linalg.norm(wavelet)
        if numpy.sum(wavelet/energy) > 1:
            print("dafuq: energy: {}, -> {}".format(energy, sum(wavelet)))
        return wavelet / energy

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
