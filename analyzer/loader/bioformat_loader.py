""" Loader for bioformat files """

from analyzer.loader.pillow_loader import PILLoader
from subprocess import check_call, Popen, PIPE
import os.path
import re
import fcntl


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

    convert_process = None
    convert_progress = '0'

    @classmethod
    def convert_bg(cls, path):
        """ Convert the file using the bioformat tools in the background.
        Returns false, if the file is already converted, true if the process
        started. """
        if cls.convert_process is not None:
            return False

        tifpath = path + '.tif'
        if os.path.isfile(tifpath):
            return False
        cls.convert_process = Popen(['./lib/bftools/bfconvert', path, tifpath],
                                    stdout=PIPE, stderr=PIPE)

        # Make interaction possible by using non blocking IO
        fcntl.fcntl(cls.convert_process.stdout.fileno(),
                    fcntl.F_SETFL, os.O_NONBLOCK)
        return True

    @classmethod
    def get_conversion_progress(cls):
        if cls.convert_process is None:
            return {'finished': True}

        returncode = cls.convert_process.poll()
        if returncode == 0:
            cls.convert_process = None
            return {'finished': True}

        if returncode != None:
            cls.convert_process = None
            print("Conversion failed with output %s!"
                  % cls.convert_process.stderr.read())
            return {'finished': True, 'error': "Conversion process failed!"}

        # The progress is of the format (x%) in the last line of output
        try:
            out = cls.convert_process.stdout.read()
            if out is not None:  # python 3 returns None if no new output
                matches = re.search(br'\((\d+)%\)', out.split(b'\n')[-2])
                if matches:
                    cls.convert_progress = matches.group(1).decode("utf-8")
        except IOError:  # python 2 gives exception if no new output
            pass

        return {'finished': False, 'progress': cls.convert_progress}
