""" Base class for a Loader, which produces frames """

import numpy

# Number of frames used to calculate average frame and pixel's variance
statistics_frame_count = 100


class Loader(object):
    """ Base class for a file loader. Implementations must overwrite
    __init__, can_open, next_frame and get_frame methods"""

    def __init__(self, path):
        """Constructor, which opens the specified path in
        implementations."""
        raise NotImplemented

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
        frames = numpy.zeros((statistics_frame_count,
                              firstFrame.shape[0],
                              firstFrame.shape[1]),
                             numpy.uint16)

        # Now we will load equidistant frames of that number
        steps = min(self.frame_count(), statistics_frame_count)
        step_size = int(self.frame_count() / steps)

        for i in range(step_size, steps, step_size):
            frames[i, :, :] = self.get_frame(i)

        self.mean = numpy.mean(frames, 0)
        self.variance = numpy.var(frames, 0)

loader_types = []


def register_loader_class(cls):
    """ Register a loader class to automatically use for correct filetypes"""
    loader_types.append(cls)


def open(path, type=None):
    """ Open a video from a path(file/directory)
    This will try to choose the correct implementation

    @param path: The path to the video file
    @param type: Which implementation to use. If None the format is
    guessed. More formats can be implemented by
    subclassing the Loader class.
    @return: A Loader object which can output frames"""

    if not type:
        for c in loader_types:
            if c.can_open(path):
                type = c

    if not type:
        raise OSError('No loader for the type of %s' % path)

    return type(path)
