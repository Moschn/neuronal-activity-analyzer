from analyzer.segmentation.segmentation import Segmentation
from skimage.feature import peak_local_max
import scipy.ndimage
import skimage.morphology
import skimage.segmentation
import numpy


class Randomwalker(Segmentation):

    def get_segmentation(self, image):
        # from http://www.scipy-lectures.org/packages/scikit-image/
        distance = scipy.ndimage.distance_transform_edt(image)
        local_maxi = peak_local_max(distance, indices=False,
                                    footprint=numpy.ones((10, 10)),
                                    labels=image)
        markers = skimage.morphology.label(local_maxi)
        markers[~image] = -1
        segmented = skimage.segmentation.random_walker(distance, markers,
                                                       beta=10, copy=False)
        segmented[segmented == -1] = 0
        return segmented
