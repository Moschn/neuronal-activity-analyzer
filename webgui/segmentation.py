import os
from threading import Lock

from flask import Blueprint, current_app, request, jsonify

import analyzer
from .runs import Run

segmentation_blueprint = Blueprint('segmentation', __name__)

# We use this lock to stop multiple requests arriving simultaniously from all
# calculating the segmentation. Just the first should calculate, the rest
# should get it from cache
segmentation_lock = Lock()


def generate_segmentation(run):
    """ Run the segmentation in the analyzer module and save the result to run's
    data
    """
    with segmentation_lock:
        loader = analyzer.open_video(
            os.path.join(current_app.config['VIDEO_FOLDER'], run.videoname))
        segmented = analyzer.segment(loader, run['config'])

        # Set the roi editor state to the automatic segmentation result
        segmented['editor'] = segmented['segmented']

        run['segmentation'] = segmented
        run['pixel_per_um'] = loader.pixel_per_um
        run['exposure_time'] = loader.exposure_time
        run['statistics'] = None
    return segmented


@segmentation_blueprint.route(
    '/set_segmentation_params/<path:videoname>/<runname>', methods=['POST'])
def set_segmentation_params(videoname, runname):
    try:
        with Run(videoname, runname) as run:
            config = run['config']
            pixel_per_um = run['pixel_per_um']
            for key in ['segmentation_source', 'gauss_radius', 'threshold',
                        'segmentation_algorithm', 'spike_detection_algorithm',
                        'nSD_n', 'threshold_applicator']:
                config[key] = request.values.get(key, config[key])
                run['config'] = config

            segmented = generate_segmentation(run)

        # Convert numpy arrays to flat lists
        response = {}
        response['segmentation'] = {}
        response['segmentation']['success'] = 'Segmentation generated'
        response['segmentation']['width'] = segmented['source'].shape[1]
        response['segmentation']['height'] = segmented['source'].shape[0]
        for k in segmented:
            response['segmentation'][k] = segmented[k].flatten().tolist()

        response['segmentation']['pixel_per_um'] = pixel_per_um
        response['config'] = config
        thresholds = analyzer.get_thresholds(segmented['filtered'])
        response['thresholds'] = thresholds

        return jsonify(response)
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_blueprint.route('/get_segmentation/<path:videoname>/<runname>')
def get_segmentation(videoname, runname):
    with Run(videoname, runname) as run:
        segmented = run['segmentation']
        pixel_per_um = run['pixel_per_um']
        config = run['config']

    response = {}
    response['segmentation'] = {}
    response['segmentation']['width'] = segmented['source'].shape[1]
    response['segmentation']['height'] = segmented['source'].shape[0]
    # Convert numpy arrays to flat lists
    for k in segmented:
        response['segmentation'][k] = segmented[k].flatten().tolist()
    response['segmentation']['pixel_per_um'] = pixel_per_um
    response['config'] = config
    response['thresholds'] = analyzer.get_thresholds(segmented['filtered'])

    return jsonify(**response)


@segmentation_blueprint.route('/get_thresholds/<path:videoname>/<runname>')
def get_thresholds(videoname, runname):
    with Run(videoname, runname) as run:
        thresholds = analyzer.get_thresholds(run['segmentation']['filtered'])
    return jsonify(**thresholds)


@segmentation_blueprint.route('/get_borders/<path:videoname>/<runname>')
def get_borders(videoname, runname):
    with Run(videoname, runname) as run:
        borders = run['segmented']['borders'].flatten().tolist()
    return jsonify(borders=borders)
