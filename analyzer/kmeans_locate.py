from analyzer.locate import Locate
import numpy
import scipy.ndimage
import skimage
from skimage.segmentation import *
from skimage.morphology import label
from matplotlib import pyplot


class K_means_locate(Locate):

    def __init__(self):
        pass

    def analyze_frame(self, frame):
        # copy numpy array, so it still stay intact for analysis
        img = numpy.copy(frame)

        # li threshold
        threshold = skimage.filters.threshold_li(img)
        img = img > threshold

        # random walker
        result = self._k_means(img)

        # If wanted the cleaned image can be displayed
        pyplot.imshow(result)
        pyplot.show()

        # result = self._findNeurons(img_thresholded)

        return result

    def _calcThreshold(self, frame, percentage):
        color_range = numpy.amax(frame) - numpy.amin(frame)
        threshold = numpy.amin(frame) + percentage*color_range
        return threshold

    def _smooth(self, frame, radius):
        return scipy.ndimage.filters.gaussian_filter(
            frame, radius, mode='nearest')

    def _k_means(self, frame):
        # labels = felzenszwalb(frame)
        labels = slic(frame, n_segments=250, compactness=0.001, sigma=0)
        # labels = label(frame, neighbors=8, background=0)
        return labels
