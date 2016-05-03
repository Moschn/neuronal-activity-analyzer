from os.path import abspath, dirname, join

ROOT_DIR = abspath(dirname(__file__))

VIDEO_FOLDER = ROOT_DIR + '/uploads'
DATA_FOLDER = ROOT_DIR + '/data'
ALLOWED_EXTENSIONS = set(['tif', 'cdx'])

SECRET_KEY = '\x96\xabV\x04\xf0\xfb\x1eii\xf7kU8Jj:\xc3\x95\xfbt\xc9x\xa8\xc8'
