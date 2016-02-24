""" Loader class using pillow """

from analyzer.loader import Loader
from PIL import Image
import numpy


class PILLoader(Loader):

    def __init__(self, path):
        self.im = Image.open(path)  # Will load first frame
        self.current_frame = -1

    @classmethod
    def can_open(cls, path):
        try:
            Image.open(path)
        except OSError:
            return False
        return True

    def next_frame(self):
        self.current_frame += 1
        self.im.seek(self.current_frame)

        return numpy.array(self.im)
