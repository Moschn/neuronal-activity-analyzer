""" Loader class using pillow """

from analyzer.loader.loader import Loader
from PIL import Image
import numpy


class PILLoader(Loader):

    def __init__(self, path):
        self.im = Image.open(path)  # Will load first frame
        self.current_frame = -1
        self.path = path

        # use the 
        super().__init__(path)

    @classmethod
    def can_open(cls, path):
        try:
            Image.open(path)
        except:
            return False
        return True

    def next_frame(self):
        self.current_frame += 1
        self.im.seek(self.current_frame)

        return numpy.array(self.im)

    def get_frame(self, index):
        self.current_frame = index
        self.im.seek(index)

        return numpy.array(self.im)

    def frame_count(self):
        return self.im.n_frames

    # def get_metadata(self):
    #     f = open(self.path, 'rb')
    #     tags = exifread.process_file(f)
    #     return tags
