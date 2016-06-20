from flask import Blueprint, jsonify, current_app
from os import path

import analyzer
from .runs import Run
from .segmentation import generate_segmentation
from .util import make_tree


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
        path.join(current_app.config['VIDEO_FOLDER'], videoname))

    return jsonify({'success': True})


@file_select_blueprint.route('/get_tree/')
def get_tree():
    return jsonify(make_tree(current_app.config['VIDEO_FOLDER']))


@file_select_blueprint.route('/get_config/<path:videoname>/<runname>')
def get_config(videoname, runname):
    with Run(videoname, runname) as run:
        config = run['config']
    return jsonify(config)
