from skimage import morphology
from analyzer.segmentation.segmentation import Segmentation


class Label(Segmentation):

    def get_segmentation(self, image):
        return morphology.label(image)
