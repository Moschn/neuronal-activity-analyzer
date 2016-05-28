""" Loader for bioformat files """

from analyzer.loader.pillow_loader import PILLoader
from subprocess import check_call
import os.path


class BioFormatLoader(PILLoader):

    def __init__(self, path):
        tifpath = path + '.tif'
        if not os.path.isfile(tifpath):
            # Convert to tif
            check_call(['./lib/bftools/bfconvert', path, tifpath])
        PILLoader.__init__(self, tifpath)

    @classmethod
    def can_open(cls, path):
        with open(path, 'rb') as f:
            magic_bytes = f.read(4)
        if magic_bytes == b'\xd0\xcf\x11\xe0':
            # Simple PCI (cxd) magic bytes
            return True

        return False
