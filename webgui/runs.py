import shelve
import os
from os import path, listdir, makedirs
from flask import current_app
from threading import Lock

import analyzer.settings

RUN_VERSION = 1


class Run():
    """ This is a version of shelf, which automatically generates the path from
    the videoname and the runname. It is used as a cache for results in between
    requests. It should be used in the with syntax. Note that multiple requests
    can not be in a such a with block at the same time, to prevent cache
    corruption. Therefore try to stay in here not too long.

    Example usage:

    with Run(videoname, runname) as run:
        run['config']['threshold'] = 0.1
    """
    lock = Lock()

    def __init__(self, videoname, runname):
        self.videoname = videoname
        self.runname = runname
        self.shelf = None

        self.runpath = self._path(self.videoname, self.runname)
        folder = path.dirname(self.runpath)
        if not path.exists(folder):
            makedirs(folder)

    def open(self):
        Run.lock.acquire()
        self.shelf = shelve.open(self.runpath, writeback=True)
        if 'config' in self.shelf:
            # The shelf already contains data
            if('version' not in self.shelf or
               self.shelf['version'] != RUN_VERSION):
                Run._update(self.shelf)

    def close(self):
        self.shelf.sync()
        self.shelf.close()
        self.shelf = None
        Run.lock.release()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __getitem__(self, key):
        if self.shelf is None:
            raise Exception("Shelf is not open!")
        return self.shelf[key]

    def __setitem__(self, key, value):
        if self.shelf is None:
            raise Exception("Shelf is not open!")
        self.shelf[key] = value

    @staticmethod
    def ls(videoname):
        folder = path.dirname(Run._path(videoname, ''))
        basename = path.basename(videoname)

        if not path.exists(folder):
            return []

        entries = [entry[len(basename) + 1:entry.rfind('.run')]
                   for entry in listdir(folder)
                   if entry.startswith(basename)]
        # remove entries appearing multiple times
        # these appear, as some systems use more than one file to store a shelf
        runs = list(set(entries))
        runs.sort()

        return runs

    @staticmethod
    def remove(videoname, runname):
        path = Run._path(videoname, runname)
        os.remove(path)

    @staticmethod
    def _path(videoname, runname):
        return path.join(current_app.config['DATA_FOLDER'],
                         videoname + "." + runname + ".run")

    @classmethod
    def _update(cls, shelf):
        if 'version' not in shelf:
            old_version = 0
        else:
            old_version = shelf['version']

        if old_version == 0:
            if shelf['config']['spike_detection_algorithm'] == 'wavelet':
                shelf['config']['spike_detection_algorithm'] = 'wdm'
            if shelf['config']['spike_detection_algorithm'] == 'nSD':
                shelf['config']['spike_detection_algorithm'] = 'ntimesstd'

            if shelf['config']['segmentation_algorithm'] == 'fill':
                shelf['config']['segmentation_algorithm'] = 'label'
            if shelf['config']['segmentation_algorithm'] == 'randomwalk':
                shelf['config']['segmentation_algorithm'] = 'randomwalker'

        for k, v in analyzer.settings.default_config.items():
            if k not in shelf['config']:
                shelf['config'][k] = v

        shelf['version'] = RUN_VERSION
