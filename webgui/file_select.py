from flask import Blueprint, jsonify, current_app, send_file
from flask import request
from os import walk
import os.path
from io import BytesIO
import zipfile
import zlib
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename

import analyzer
from .runs import Run
from .segmentation import generate_segmentation
from .util import make_tree

ALLOWED_EXTENSIONS = set(['tif', '.cxd'])

file_select_blueprint = Blueprint('file_select', __name__)


@file_select_blueprint.route('/get_runs/<path:videoname>')
def get_runs(videoname):
    try:
        if videoname.endswith('.tif'):
            return jsonify(runs=Run.ls(videoname))
        elif videoname.endswith('.cxd'):
            return jsonify(error='need_conversion')
        else:
            return jsonify(error='is_folder')
    except Exception as e:
        return jsonify(error=str(e))


@file_select_blueprint.route('/create_run/<path:videoname>/<runname>',
                             methods=['POST'])
def create_run(videoname, runname):
    if runname in Run.ls(videoname):
        return jsonify(error="A run with that name already exists!")

    with Run(videoname, runname) as run:
        config = analyzer.util.get_default_config()

        run['config'] = config
        generate_segmentation(run)

    return jsonify(success=True, runs=Run.ls(videoname))


@file_select_blueprint.route('/delete_run/<path:videoname>/<runname>',
                             methods=['POST'])
def delete_run(videoname, runname):
    try:
        Run.remove(videoname, runname)
        return jsonify({'runs': Run.ls(videoname)})
    except Exception as e:
        return jsonify({'fail': str(e)})


@file_select_blueprint.route('/convert/<path:videoname>', methods=['POST'])
def convert(videoname):
    # We convert by opening the file
    analyzer.open_video(
        os.path.join(current_app.config['VIDEO_FOLDER'], videoname))

    return jsonify({'success': True})


@file_select_blueprint.route('/get_tree/')
def get_tree():
    return jsonify(make_tree(current_app.config['VIDEO_FOLDER']))


@file_select_blueprint.route('/get_config/<path:videoname>/<runname>')
def get_config(videoname, runname):
    with Run(videoname, runname) as run:
        config = run['config']
    return jsonify(config)


@file_select_blueprint.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    path = safe_join(current_app.config['VIDEO_FOLDER'], filename)
    print(path)
    if not os.path.isfile(path):
        # zip the folder
        zip_in_memory = BytesIO()
        with zipfile.ZipFile(zip_in_memory, 'w',
                             compression=zipfile.ZIP_DEFLATED, ) as zf:
            for dirpath, dirs, files in walk(path):
                for f in files:
                    fn = os.path.join(dirpath, f)
                    zf.write(fn, os.path.relpath(fn, path))

        zip_in_memory.seek(0)
        zipname = os.path.basename(path) + '.zip'
        return send_file(zip_in_memory, attachment_filename=zipname,
                         as_attachment=True)
    else:
        return send_file(path, attachment_filename=os.path.basename(path),
                         as_attachment=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@file_select_blueprint.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        response = {}
        response['files'] = {}
        response['files']['name'] = 'empty'
        response['files']['size'] = '0'
        response['files']['error'] = 'No file part'
        return jsonify(response)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        response = {}
        response['files'] = {}
        response['files']['name'] = 'empty'
        response['files']['size'] = '0'
        response['files']['error'] = 'No selected file'
        return jsonify(response)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                               "upload",
                               filename))
        response = {}
        response['files'] = {}
        response['files']['name'] = filename
        response['files']['size'] = os.stat(filename)
        response['files']['url'] = '/download/' + filename
        # response['files']['thumbnailUrl'] = '/favicon.ico'
        return jsonify(response)
