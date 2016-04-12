from analyzer.locate import Locate
import numpy
import scipy.ndimage
import skimage
from skimage.morphology import watershed
from skimage.feature import peak_local_max

from matplotlib import pyplot
from matplotlib import gridspec
import matplotlib.cm as cm


class Watershed_locate(Locate):

    def __init__(self, watershed=1, threshold=1):
        self.watershed = watershed
        self.threshold = threshold
        pass

    def analyze_frame(self, frame):
        # copy numpy array, so it still stay intact for analysis
        img = numpy.copy(frame)

        # img = scipy.ndimage.filters.gaussian_filter(img, 1)
        # li threshold
        if self.threshold > 0:
            threshold = skimage.filters.threshold_li(img)
            img = img > threshold

        # watershed
        if self.watershed > 0:
            result = self._watershed(img)

        # If wanted the cleaned image can be displayed
        # pyplot.imshow(result)
        # pyplot.show()

        # result = self._findNeurons(img_thresholded)

        return result

    def _calcThreshold(self, frame, percentage):
        color_range = numpy.amax(frame) - numpy.amin(frame)
        threshold = numpy.amin(frame) + percentage*color_range
        return threshold

    def _smooth(self, frame, radius):
        return scipy.ndimage.filters.gaussian_filter(
            frame, radius, mode='nearest')

    def _watershed(self, frame):
        # from http://www.scipy-lectures.org/packages/scikit-image/
        distance = scipy.ndimage.distance_transform_edt(frame)
        local_maxi = peak_local_max(distance, indices=False,
                                    footprint=numpy.ones((15, 15)),
                                    labels=frame)
        markers = skimage.morphology.label(local_maxi)
        labels = watershed(-distance, markers, mask=frame)
        
        return labels
