from os.path import abspath, dirname, join, isfile
from os import listdir
import shelve

from flask import current_app, g

ROOT_DIR = abspath(dirname(__file__))

def check_extension(filename, allowed):
    """ Checks if the filename ends with an extension in the allowed list """
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed

def session_save(videoname, key, value):
    path = join(current_app.config['DATA_FOLDER'],
                "%s-%s.session" % (videoname, g.session))
    with shelve.open(path, writeback=True) as shelf:
        shelf[key] = value

def session_load(videoname, key):
    path = join(current_app.config['DATA_FOLDER'],
                "%s-%s.session" % (videoname, g.session))
    if not isfile(path):
        return None
    with shelve.open(path) as shelf:
        print("loaded session:")
        print(dict(shelf))
        if key in shelf:
            return shelf[key]
        return None

def list_sessions(videoname):
    files = listdir(current_app.config['DATA_FOLDER'])
    sessions = [ name[len(videoname)+1:-8] for name in files
                 if name.startswith(videoname) ]
    return sessions

def cache_load(videoname, params, key):
    path = get_filename(videoname, params, 'cache', 'cache')
    if not isfile(path):
        return None
    
    with shelve.open(path) as shelf:
        if key in shelf:
            return shelf[key]
        return None

def cache_save(videoname, params, key, value):
    path = get_filename(videoname, params, 'cache', 'cache')
    with shelve.open(path, writeback=True) as shelf:
        shelf[key] = value

def get_filename(videoname, params, tag, ext):
    """ Generates a filename in the cachefolder, which will be the same next time
    if the same params, videoname, tag and ext is provided """
    name = '%s-%i-%s.%s' % (
        videoname,
        hash(frozenset(sorted(params.items()))),
        tag,
        ext)
    return join(current_app.config['CACHE_FOLDER'], name)
