""" Hard threshold implementation """
import numpy
from .apply_threshold import ApplyThreshold


class HardThreshold(ApplyThreshold):

    def apply_threshold(self, loader, image, threshold):
        color_range = numpy.amax(image) - numpy.amin(image)
        abs_threshold = numpy.amin(image) + threshold*color_range
        return image > abs_threshold
