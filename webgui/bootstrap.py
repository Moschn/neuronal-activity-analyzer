from flask import Flask
import os

from .segmentation_page import segmentation_page
from .roi_editor import roi_editor
from .statistics import statistics
from .util import ROOT_DIR

def create_app():
    app = Flask('Neuronal activity analyzer',
                template_folder='templates',
                static_folder='webgui/static')
    app.config.from_pyfile('webconfig.py')
    app.secret_key = app.config['SECRET_KEY']

    # Create folders if they don't exist
    folders = [app.config['VIDEO_FOLDER'],
               app.config['CACHE_FOLDER'],
               app.config['DATA_FOLDER']]
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        
    app.register_blueprint(segmentation_page)
    app.register_blueprint(roi_editor)
    app.register_blueprint(statistics)

    return app
