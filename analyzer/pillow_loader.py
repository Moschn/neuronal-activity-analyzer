""" Loader class using pillow """

from analyzer.loader import Loader
from PIL import Image
import numpy
import exifread
import os


class PILLoader(Loader):

    def __init__(self, path):
        self.im = Image.open(path)  # Will load first frame
        self.current_frame = -1
        self.path = path

        conf_name = path + ".txt"
        try:
            if os.path.isfile(conf_name):
                f = open(conf_name, 'r')
                for line in f:
                    parts = line.split("=")
                    if "FrameRate" in parts[0]:
                        frame_rate = float(parts[len(parts)-1].strip())
                        self.exposure_time = 1/frame_rate
                    if "PixelPerUM" in parts[0]:
                        self.pixel_per_um = float(parts[len(parts)-1].strip())
        except:
            if os.stat(path).st_size > 100000000:
                print("Could not open or convert the config file of " + path)
                print("FrameRate is set to standard: 31.9 fps")
                print("PixelPerUM is set to standard: 0.6466")        

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

    def get_metadata(self):
        f = open(self.path, 'rb')
        tags = exifread.process_file(f)
        return tags
