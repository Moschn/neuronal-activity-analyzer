import skimage
import scipy.ndimage.filters


def threshold(image, thresh):
    return image > thresh


def threshold_li(image):
    thresh = skimage.filters.threshold_li(image)
    return threshold(image, thresh)


def threshold_otsu(image):
    thresh = skimage.filters.threshold_otsu(image)
    return threshold(image, thresh)


def threshold_yen(image):
    thresh = skimage.filters.threshold_yen(image)
    return threshold(image, thresh)


def threshold_otsu_local(image, radius=3):
    selem = skimage.morphology.disk(radius)
    local_otsu_thresh = skimage.filters.rank.otsu(image, selem)
    return image >= local_otsu_thresh


def gauss_filter(image, radius=5):
    return scipy.ndimage.filters.gaussian_filter(image, radius,
                                                   mode='nearest')
