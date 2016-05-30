from skimage.filters import threshold_yen
from analyzer.threshold.threshold import Threshold


class Yen(Threshold):

    def get_threshold(self, image):
        return Threshold.color_in_range(image, threshold_yen(image))
