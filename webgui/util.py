import os
import shelve
import numpy
import time
from base64 import b64decode

from flask import current_app, g

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


def check_extension(filename, allowed):
    """ Checks if the filename ends with an extension in the allowed list """
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed


def run_path(videoname, runname):
    return os.path.join(current_app.config['DATA_FOLDER'],
                "%s-%s.run" % (videoname, runname))


def run_save(videoname, key, value):
    path = run_path(videoname, g.run)
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with shelve.open(path, writeback=True) as shelf:
        shelf[key] = value


def run_load(videoname, key):
    path = run_path(videoname, g.run)
    print(path)
    if not os.path.isfile(path):
        return None
    try:
        with shelve.open(path) as shelf:
            if key in shelf:
                return shelf[key]
            return None
    except:
        time.sleep(0.3)
        return run_load(videoname, key)


def list_runs(videoname):
    path = os.path.dirname(videoname)
    basename = os.path.basename(videoname)
    files = os.listdir(os.path.join(current_app.config['DATA_FOLDER'],
                                    path))
    runs = [name[len(basename)+1:-4] for name in files
            if name.startswith(basename)]
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
