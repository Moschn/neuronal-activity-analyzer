""" Base class for a Loader, which produces frames """

import numpy
import analyzer.util
import os

# Number of frames used to calculate average frame and pixel's variance
statistics_frame_count = 100


class Loader(object):
    """ Base class for a file loader. Implementations must overwrite
    __init__, can_open, next_frame and get_frame methods"""

    def __init__(self, path):
        """Constructor, which opens the specified path in
        implementations. If super().__init__(path) is called then
        the default video specific configureation file is loaded"""
        self.exposure_time = 0.031347962382445145  # 1 / 31.9 fps
        self.pixel_per_um = 0.6466

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
        """ Return if the implementation can parse data at the
        specified path"""

        raise NotImplemented

    def next_frame(self):
        """ Overwriten in implementation

        @returns: numpy array [height][width] containing pixel data

        @throws: EndOfFile if no more frames are available
        """

        raise NotImplemented

    def get_frame(self, index):
        """ Overwritten in implementation

        @returns: numpy array [height][width] containing pixel data

        @throws: EndOfFile if frame is not available
        """

        raise NotImplemented

    def frame_count(self):
        """ Returns the number of frames """
        raise NotImplemented

    def get_metadata(self):
        """ Returns the metadata embedded in the image in a dictionary"""
        raise NotImplemented

    def get_mean(self):
        """Get the average frame of 100 equidistant frames over the sequence.
        Destroys the internal frame index"""

        if not hasattr(self, 'mean'):
            self._calculate_statistics()

        return self.mean

    def get_variance(self):
        """Get one numpy array, same shape as the image, describing the variance
        of each pixel"""

        if not hasattr(self, 'variance'):
            self._calculate_statistics()

        return self.variance

    def _calculate_statistics(self):
        """Calculates average frame and variance"""
        # We reserve space for statistics_frame_count frames
        firstFrame = self.get_frame(0)

        # Now we will load equidistant frames of that number
        steps = min(self.frame_count(), statistics_frame_count)
        step_size = int(self.frame_count() / steps)

        frames = numpy.zeros((steps,
                              firstFrame.shape[0],
                              firstFrame.shape[1]),
                             numpy.uint16)

        for i in range(0, steps):
            frames[i, :, :] = self.get_frame(i*step_size)

        self.mean = numpy.mean(frames, axis=0)
        self.variance = numpy.var(frames, axis=0)

    @classmethod
    def find_loader_class(cls):
        """ Register all loader class to automatically use for correct filetypes
        """
        load_classes = analyzer.util.list_implementations(analyzer.loader, cls)
        for k, v in load_classes.items():
            loader_types.append(v)

loader_types = []


def open(path, typ=None):
    """ Open a video from a path(file/directory)
    This will try to choose the correct implementation

    @param path: The path to the video file
    @param type: Which implementation to use. If None the format is
    guessed. More formats can be implemented by
    subclassing the Loader class.
    @return: A Loader object which can output frames"""
    if typ is None:
        for c in loader_types:
            if c.can_open(path):
                typ = c

    if typ is None:
        raise OSError('No loader for the type of %s' % path)

    return typ(path)
