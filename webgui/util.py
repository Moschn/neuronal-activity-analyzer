import os
import shelve
import numpy
import time
from base64 import b64decode

from flask import current_app, g

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EXTENSIONS = {".run", ".run.db", ".run.dat"}


def check_extension(filename):
    """ Checks if the filename ends with an extension in the allowed list """
    for extension in ALLOWED_EXTENSIONS:
        if filename.endswith(extension):
            return True
    return False


def strip_allowed_extension(filename):
    for extension in ALLOWED_EXTENSIONS:
        if filename.endswith(extension):
            return filename[0:-len(extension)]
    return False


def run_path(videoname, runname):
    dirname = os.path.join(current_app.config['DATA_FOLDER'],
                           os.path.dirname(videoname))
    for filename in os.listdir(dirname):
        if runname in filename.split(".") and check_extension(filename):
            return os.path.join(dirname, filename)
    return False


def run_save(videoname, key, value):
    path = os.path.join(current_app.config['DATA_FOLDER'],
                        videoname + "." + g.run + ".run")

    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with shelve.open(path, writeback=True) as shelf:
        shelf[key] = value


def run_load(videoname, key, n=0):
    path = run_path(videoname, g.run)
    if not os.path.isfile(path):
        return None
    if path.endswith(".db"):
        path = path[0:-3]
    try:
        with shelve.open(path) as shelf:
            if key in shelf:
                return shelf[key]
            return None
    except:
        # ugly hack. Shelve sometimes say resource not available :(
        time.sleep(0.3)
        if n > 50:
            raise Exception("shelve did not open")
        return run_load(videoname, key, n+1)


def list_runs(videoname):
    path = os.path.join(current_app.config['DATA_FOLDER'],
                        os.path.dirname(videoname))
    runs = []
    basename = os.path.basename(videoname)
    for filename in os.listdir(path):
        if check_extension(filename) and basename in filename:
            complete_name = strip_allowed_extension(os.path.basename(filename))
            runs.append(complete_name.split(".")[-1])
    return runs


def run_delete(videoname, runname):
    path = run_path(videoname, runname)
    os.remove(path)


def decode_array_8(data, w, h):
    decoded = b64decode(data)
    return numpy.frombuffer(decoded, dtype='uint8').reshape(w, h)


def make_tree(path_arg):
    tree = dict(name=os.path.basename(path_arg), children=[])
    try:
        lst = os.listdir(path_arg)
    except OSError:
        print("dafuq")
        pass  # ignore errors
    else:
        for name in lst:
            fn = os.path.join(path_arg, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name))
    return tree
