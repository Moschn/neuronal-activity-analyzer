from os import listdir
import os
from threading import Lock
import numpy

from flask import Blueprint, current_app, request, redirect, url_for
from flask import render_template, flash, jsonify, g
from werkzeug import secure_filename

import analyzer
from .util import check_extension, run_save, run_load, list_runs, run_delete
from .util import decode_array_8

import mpld3

segmentation_page = Blueprint('segmentation', __name__,
                              template_folder='templates')

# We use this lock to stop multiple requests arriving simultaniously from all
# calculating the segmentation. Just the first should calculate, the rest
# should get it from cache
segmentation_lock = Lock()


@segmentation_page.route('/set_edited_segmentation/<videoname>/<runname>',
                         methods=['POST'])
def set_edited_segmentation(videoname, runname):
    try:
        g.run = runname
        segmented = run_load(videoname, 'segmentation')

        encoded_data = request.values.get('edited_segmentation')
        edited_seg = decode_array_8(encoded_data,
                                    segmented['editor'].shape[0],
                                    segmented['editor'].shape[1])
        unique_neurons = numpy.unique(edited_seg)[1:]  # 0 is background
        filled_seg = numpy.zeros(edited_seg.shape, dtype='uint8')
        n = 1
        for i in unique_neurons:
            filled_seg[edited_seg == i] = n
            n += 1
        segmented['editor'] = filled_seg
        print(numpy.amax(filled_seg))

        run_save(videoname, 'segmentation', segmented)
        run_save(videoname, 'statistics', None)  # Invalidate statistics
        return jsonify(success=True)
    except Exception as e:
        return jsonify(fail=str(e))


def generate_segmentation(videoname, config):
    """ Run the segmentation in the analyzer module and save the result to run's
    data
    """
    with segmentation_lock:
        loader = analyzer.loader.open(
            os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
        segmented = analyzer.segment(loader, config)

        # Set the roi editor state to the automatic segmentation result
        segmented['editor'] = segmented['segmented']

        run_save(videoname, 'segmentation', segmented)
        run_save(videoname, 'pixel_per_um', loader.pixel_per_um)
        run_save(videoname, 'statistics', None)

    return segmented


@segmentation_page.route('/set_segmentation_params/<videoname>/<runname>',
                         methods=['POST'])
def set_segmentation_params(videoname, runname):
    try:
        g.run = runname

        config = run_load(videoname, 'config')
        for key in ['segmentation_source', 'gauss_radius', 'threshold',
                    'segmentation_algorithm']:
            config[key] = request.values.get(key, config[key])
        run_save(videoname, 'config', config)

        segmented = generate_segmentation(videoname, config)

        # Convert numpy arrays to flat lists
        response = {}
        response['success'] = 'Segmentation generated'
        response['width'] = segmented['source'].shape[0]
        response['height'] = segmented['source'].shape[1]
        for k in segmented:
            response[k] = segmented[k].flatten().tolist()
        return jsonify(response)
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/get_segmentation/<videoname>/<runname>')
def get_segmentation(videoname, runname):
    g.run = runname
    segmented = run_load(videoname, 'segmentation')
    pixel_per_um = run_load(videoname, 'pixel_per_um')

    # Convert numpy arrays to flat lists
    response = {}
    response['width'] = segmented['source'].shape[0]
    response['height'] = segmented['source'].shape[1]
    for k in segmented:
        response[k] = segmented[k].flatten().tolist()

    fig_roi = analyzer.plot.plot_roi(segmented['segmented'],
                                     segmented['source'],
                                     pixel_per_um)
    response['roi'] = mpld3.fig_to_dict(fig_roi)
    return jsonify(response)


@segmentation_page.route('/create_run/<videoname>/<runname>',
                         methods=['POST'])
def create_run(videoname, runname):
    g.run = runname
    config = analyzer.util.get_default_config()

    run_save(videoname, 'config', config)
    generate_segmentation(videoname, config)

    return jsonify({'runs': list_runs(videoname)})


@segmentation_page.route('/delete_run/<videoname>/<runname>',
                         methods=['DELETE'])
def delete_run(videoname, runname):
    try:
        run_delete(videoname, runname)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/get_runs/<videoname>')
def get_runs(videoname):
    return jsonify({'runs': list_runs(videoname)})


@segmentation_page.route('/get_thresholds/<videoname>/<runname>')
def get_thresholds(videoname, runname):
    g.run = runname
    segmented = run_load(videoname, 'segmentation')
    thresholds = analyzer.get_thresholds(segmented['filtered'])
    return jsonify(**thresholds)


@segmentation_page.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['uploaded_file']
    if file and check_extension(file.filename,
                                current_app.config['ALLOWED_EXTENSIONS']):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['VIDEO_FOLDER'], filename))
        flash('File %s was uploaded!' % filename)
        return redirect(url_for('segmentation.main_page'))


@segmentation_page.route('/')
@segmentation_page.route('/segmentation')
def main_page():
    files = listdir(current_app.config['VIDEO_FOLDER'])
    return render_template('main.html',
                           files=files)
