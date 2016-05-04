from os.path import abspath, dirname, join, isfile
from os import listdir, remove
import shelve

from flask import current_app, g

ROOT_DIR = abspath(dirname(__file__))


def check_extension(filename, allowed):
    """ Checks if the filename ends with an extension in the allowed list """
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed


def run_path(videoname, runname):
    return join(current_app.config['DATA_FOLDER'],
                "%s-%s.run" % (videoname, runname))


def run_save(videoname, key, value):
    path = run_path(videoname, g.run)
    with shelve.open(path, writeback=True) as shelf:
        shelf[key] = value


def run_load(videoname, key):
    path = run_path(videoname, g.run)
    if not isfile(path):
        return None
    with shelve.open(path) as shelf:
        if key in shelf:
            return shelf[key]
        return None


def list_runs(videoname):
    files = listdir(current_app.config['DATA_FOLDER'])
    runs = [name[len(videoname)+1:-4] for name in files
            if name.startswith(videoname)]
    return runs


def run_delete(videoname, runname):
    path = run_path(videoname, runname)
    remove(path)
