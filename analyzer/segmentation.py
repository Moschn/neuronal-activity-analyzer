import numpy
import scipy.ndimage
import skimage
import skimage.morphology
from skimage.feature import peak_local_max
from skimage import segmentation
from skimage.filters import threshold_li, threshold_otsu, threshold_yen

#
# Smoothing
#


def gaussian_filter(image, radius):
    return scipy.ndimage.filters.gaussian_filter(image, radius, mode='nearest')

#
# Thresholding
#


def color_in_range(image, c):
    """ Returns  where in between the darkest and brightest pixel in image the
    color c is. If c is the same as darkest, returns 0, for brightest 1, for
    brighter > 1, for darker than the darkest pixel < 0 """
    min = numpy.amin(image)
    range = numpy.amax(image) - min
    return (c - min) / range


def li_thresh_relative(image):
    """ Returns from 0 to 1 where in the dynamic range of image the li threshold
    is """
    return color_in_range(image, threshold_li(image))


def otsu_thresh_relative(image):
    """ Returns from 0 to 1 where in the dynamic range of image the otsu threshold
    is """
    return color_in_range(image, threshold_otsu(image))


def yen_thresh_relative(image):
    """ Returns from 0 to 1 where in the dynamic range of image the yen threshold
    is """
    return color_in_range(image, threshold_yen(image))


def threshold(image, percentage):
    color_range = numpy.amax(image) - numpy.amin(image)
    threshold = numpy.amin(image) + percentage*color_range
    return image > threshold

#
# Segmentation
#


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

def get_borders(roi):
    return segmentation.find_boundaries(roi);
