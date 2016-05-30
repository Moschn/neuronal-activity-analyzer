from skimage.filters import threshold_li
from analyzer.threshold.threshold import Threshold


class Li(Threshold):

    def get_threshold(self, image):
        return Threshold.color_in_range(image, threshold_li(image))
