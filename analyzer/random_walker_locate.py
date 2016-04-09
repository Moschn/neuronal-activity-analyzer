from analyzer.locate import Locate
import numpy
import scipy.ndimage
import skimage
from skimage.feature import peak_local_max
from matplotlib import pyplot


class Random_walker_locate(Locate):

    def __init__(self, random_walker=1, threshold=1):
        self.random_walker = random_walker
        self.threshold = threshold
        pass

    def analyze_frame(self, frame):
        # copy numpy array, so it still stay intact for analysis
        img = numpy.copy(frame)

        # img = self._smooth(frame, 1)
        # li threshold
        if self.threshold > 0:
            threshold = skimage.filters.threshold_li(img)
            img = img > threshold

        # random walker
        if self.random_walker > 0:
            result = self._random_walker(img)

        # If wanted the cleaned image can be displayed
        pyplot.imshow(result)
        pyplot.show()

        return result

    def _smooth(self, frame, radius):
        return scipy.ndimage.filters.gaussian_filter(
            frame, radius, mode='nearest')

    def _random_walker(self, frame):
        # from http://www.scipy-lectures.org/packages/scikit-image/
        distance = scipy.ndimage.distance_transform_edt(frame)
        local_maxi = peak_local_max(distance, indices=False,
                                    footprint=numpy.ones((10, 10)),
                                    labels=frame)
        markers = skimage.morphology.label(local_maxi)

        from skimage import segmentation
        markers[~frame] = -1
        return segmentation.random_walker(frame, markers)
