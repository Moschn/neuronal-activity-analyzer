""" Base class for a integration/sum of the pixels """
from threading import Lock
import numpy

from analyzer.settings import THREAD_COUNT


class Integrater(object):
    """ Base class for an algorithm that sums or integrates (or anything does
    anything else) the brightness of the regions of interest (ROIs) """

    def __init__(self, roi):
        """ Contructor. An array representing the various ROIs is needed.
        The array contains a number at every ROI. The number represents the
        unique nmumber of the respective ROI """
        self.roi = roi

    def process_frame(self, frame):
        """ Process new frame
        @param frame: Numpy array of the new frame

        @returns: list of all ROIs with a respective activity measure. """

        raise NotImplemented

    def get_progress(self):
        """ Get the progress while process_parallel_frames is running """
        if not hasattr(self, 'progress_lock'):
            return (0, 0)

        with self.progress_lock:
            return (self.progress_frames, self.frame_count)

    def process_parallel_frames(self, loader):
        try:  # python 3.5
            from concurrent.futures import ThreadPoolExecutor
            self.frame_count = loader.frame_count()
            activities = numpy.zeros((self.frame_count, numpy.amax(self.roi)))
            loader.lock = Lock()

            self.progress_lock = Lock()
            self.progress_frames = 0

            with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
                futures = [executor.submit(self._load_process_frame, loader, i)
                           for i in range(0, self.frame_count)]
                for future in futures:
                    (index, activity) = future.result()
                    activities[index, :] = activity
            return activities.T
        except ImportError:
            frame_count = loader.frame_count()
            activities = numpy.zeros((frame_count, numpy.max(self.roi)))
            loader.lock = Lock()
            for i in range(0, frame_count):
                index, activity = self._load_process_frame(loader, i)
                activities[index, :] = activity
            return activities.T

    def _load_process_frame(self, loader, idx):
        with loader.lock:
            frame = loader.get_frame(idx)
        processed = self.process_frame(frame)
        if(hasattr(self, 'progress_lock')):
            with self.progress_lock:
                self.progress_frames += 1
        return (idx, processed)
