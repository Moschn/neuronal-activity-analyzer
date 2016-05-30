from skimage.filters import threshold_otsu
from analyzer.threshold.threshold import Threshold


class Otsu(Threshold):

    def get_threshold(self, image):
        return Threshold.color_in_range(image, threshold_otsu(image))
