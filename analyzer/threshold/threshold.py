""" Base class for thresholds. This is not needed but should help someone who 
wants to implement their own threshold algorithm """
import numpy
import scipy.ndimage
import skimage.segmentation


class Threshold():

    def get_threshold(self, image):
        """ This function returns the threshold of image in percent of the
        greyscale"""
        pass

    @staticmethod
    def color_in_range(image, c):
        """ Returns  where in between the darkest and brightest pixel in image the
        color c is. If c is the same as darkest, returns 0, for brightest 1, for
        brighter > 1, for darker than the darkest pixel < 0 """
        min = numpy.amin(image)
        range = numpy.amax(image) - min
        return (c - min) / range

    @staticmethod
    def threshold(image, percentage):
        color_range = numpy.amax(image) - numpy.amin(image)
        threshold = numpy.amin(image) + percentage*color_range
        return image > threshold

    @staticmethod
    def gaussian_filter(image, radius):
        return scipy.ndimage.filters.gaussian_filter(image, radius, mode='nearest')

    @staticmethod
    def get_borders(roi):
        return skimage.segmentation.find_boundaries(roi)
