import numpy
import scipy.ndimage
import skimage
from skimage.morphology import label
import skimage.morphology
from skimage.feature import peak_local_max

def gaussian_filter(image, radius):
    return scipy.ndimage.filters.gaussian_filter(image, radius, mode='nearest')

def threshold(image, percentage):
    color_range = numpy.amax(image) - numpy.amin(image)
    threshold = numpy.amin(image) + percentage*color_range
    return image > threshold

def watershed(image):
        # from http://www.scipy-lectures.org/packages/scikit-image/
        distance = scipy.ndimage.distance_transform_edt(image)
        local_maxi = peak_local_max(distance, indices=False,
                                    footprint=numpy.ones((10, 10)),
                                    labels=image)
        markers = skimage.morphology.label(local_maxi)
        labels = skimage.morphology.watershed(-distance, markers, mask=image)

        return labels
