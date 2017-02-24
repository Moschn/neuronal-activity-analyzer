""" Base class for thresholds. This is not needed but should help someone who
wants to implement their own threshold algorithm """
import numpy
import scipy.ndimage
import skimage.segmentation


class ApplyThreshold(object):

    def apply_threshold(self, loader, image, threshold):
        raise NotImplemented()
