import os
import numpy
from base64 import b64decode


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EXTENSIONS = {".run", ".run.db", ".run.dat"}
STRIPED_EXTENSIONS = {".db", ".dat"}


def decode_array_8(data, w, h):
    decoded = b64decode(data)
    return numpy.frombuffer(decoded, dtype='uint8').reshape(w, h)


def make_tree(path_arg):
    tree = dict(text=os.path.basename(path_arg), nodes=[])
    try:
        lst = os.scandir(path_arg)
    except OSError:
        print("Warning: Failed to list directory: %s" % path_arg)
        pass  # ignore errors
    else:
        for entry in lst:
            fn = os.path.join(path_arg, entry.name)
            if os.path.isdir(fn):
                subtree = make_tree(fn)
                if subtree:
                    tree['nodes'].append(subtree)
            else:
                if entry.name.endswith(".tif") or entry.name.endswith(".cxd"):
                    tree['nodes'].append(dict(text=entry.name))
    if not tree['nodes']:
        return {}
    return tree

""" This functions returns the size of the given folder in bytes """
def folder_size(path):
    lst = os.scandir(path)
    size = 0
    for entry in lst:
        fn = os.path.join(path, entry.name)
        if os.path.isdir(fn):
            size += folder_size(fn)
        else:
            size += os.path.getsize(fn)
    return size
