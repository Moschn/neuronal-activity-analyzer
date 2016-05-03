from flask import Flask
import os

from .segmentation_page import segmentation_page
from .statistics import statistics


def disable_cache(response):
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


def create_app():
    app = Flask('Neuronal activity analyzer',
                template_folder='templates',
                static_folder='webgui/static')
    app.config.from_pyfile('webconfig.py')
    app.secret_key = app.config['SECRET_KEY']

    # Create folders if they don't exist
    folders = [app.config['VIDEO_FOLDER'],
               app.config['DATA_FOLDER']]
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)

    app.register_blueprint(segmentation_page)
    app.register_blueprint(statistics)

    app.after_request(disable_cache)

    return app
