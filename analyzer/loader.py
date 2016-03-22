""" Base class for a Loader, which produces frames """


class Loader(object):
    """ Base class for a file loader. Implementations must overwrite
    all methods"""

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
