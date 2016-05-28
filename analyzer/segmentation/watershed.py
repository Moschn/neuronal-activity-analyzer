from analyzer.segmentation.segmentation import Segmentation
from skimage.feature import peak_local_max
import scipy.ndimage
import skimage.morphology
import numpy


class Watershed(Segmentation):

    def get_segmentation(self, image):
        # from http://www.scipy-lectures.org/packages/scikit-image/
        distance = scipy.ndimage.distance_transform_edt(image)
        local_maxi = peak_local_max(distance, indices=False,
                                    footprint=numpy.ones((10, 10)),
                                    labels=image)
        markers = skimage.morphology.label(local_maxi)
        labels = skimage.morphology.watershed(-distance, markers, mask=image)

        return labels
