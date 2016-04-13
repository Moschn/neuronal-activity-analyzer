import numpy
import scipy.ndimage
import skimage
import skimage.morphology
from skimage.feature import peak_local_max
from skimage import segmentation


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


def random_walker(frame):
    # from http://www.scipy-lectures.org/packages/scikit-image/
    distance = scipy.ndimage.distance_transform_edt(frame)
    local_maxi = peak_local_max(distance, indices=False,
                                footprint=numpy.ones((10, 10)),
                                labels=frame)
    markers = skimage.morphology.label(local_maxi)

    markers[~frame] = -1
    return segmentation.random_walker(frame, markers)


def label(frame):
    return skimage.morphology.label(frame)


def k_means(frame):
    labels = segmentation.slic(frame, n_segments=250, compactness=0.001,
                               sigma=0)
    return labels
