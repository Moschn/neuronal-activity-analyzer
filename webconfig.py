from os.path import abspath, dirname, join

ROOT_DIR = abspath(dirname(__file__))

VIDEO_FOLDER = join(ROOT_DIR, 'uploads')
UPLOAD_FOLDER = join(VIDEO_FOLDER, 'upload')
DATA_FOLDER = join(ROOT_DIR, 'data')

UPLOAD_MAX_SIZE = 200000000000  # 200gb

SECRET_KEY = '\x96\xabV\x04\xf0\xfb\x1eii\xf7kU8Jj:\xc3\x95\xfbt\xc9x\xa8\xc8'

# Hide batch and save to NAS buttons
DEMO_MODE = False
