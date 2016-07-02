from flask import Flask
from flask.ext.compress import Compress
import os

from .main import main_blueprint
from .file_select import file_select_blueprint
from .segmentation import segmentation_blueprint
from .roi_editor import roi_editor_blueprint
from .batch import batch_blueprint
from .statistics import statistics_blueprint

compress = Compress()


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
               app.config['UPLOAD_FOLDER'],
               app.config['DATA_FOLDER']]
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(file_select_blueprint)
    app.register_blueprint(segmentation_blueprint)
    app.register_blueprint(roi_editor_blueprint)
    app.register_blueprint(statistics_blueprint)
    app.register_blueprint(batch_blueprint)

    app.after_request(disable_cache)

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    compress.init_app(app)

    return app
