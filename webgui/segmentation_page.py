from os import listdir
import os
from threading import Lock
import numpy

from flask import Blueprint, current_app, request, redirect, url_for
from flask import render_template, flash, jsonify, g
from werkzeug import secure_filename

import analyzer
from .util import check_extension, run_save, run_load, list_runs, run_delete
from .util import decode_array_8, make_tree, run_load_multiple
import webgui.batch

import mpld3

segmentation_page = Blueprint('segmentation', __name__,
                              template_folder='templates')

# We use this lock to stop multiple requests arriving simultaniously from all
# calculating the segmentation. Just the first should calculate, the rest
# should get it from cache
segmentation_lock = Lock()


@segmentation_page.route('/start_batch/<path:videoname>/<runname>', methods=['POST'])
def start_batch(videoname, runname):
    try:
        g.run = runname
    
        folder = os.path.join(current_app.config['VIDEO_FOLDER'],
                              request.form['batch_folder'])
        config = run_load(videoname, 'config')
        
        webgui.batch.start_batch(folder, config)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/stop_batch', methods=['POST'])
def stop_batch():
    """ Endpoint to stop the runnning batch process. Notice, that this just
    messages the batch thread to stop, but the batch process can only process
    the message after finishing the current file it is working on """
    print("Stopping batch...")
    try:
        webgui.batch.stop_batch()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/get_batch_progress')
def get_batch_progress():
    try:
        processed, num_files, errors = webgui.batch.get_progress()
        return jsonify({'success': True,
                        'num_files': num_files,
                        'processed_files': processed,
                        'errors': errors})
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/set_edited_segmentation/<path:videoname>/<runname>',
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

        segmented['borders'] = analyzer.segmentation\
                                       .get_borders(segmented['editor'])

        run_save(videoname, 'segmentation', segmented)
        run_save(videoname, 'statistics', None)  # Invalidate statistics
        return jsonify(success=True)
    except Exception as e:
        return jsonify(fail=str(e))


def generate_segmentation(videoname, config):
    """ Run the segmentation in the analyzer module and save the result to run's
    data
    """
    print(videoname)
    with segmentation_lock:
        loader = analyzer.loader.open(
            os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
        segmented = analyzer.segment(loader, config)

        # Set the roi editor state to the automatic segmentation result
        segmented['editor'] = segmented['segmented']

        run_save(videoname, 'segmentation', segmented)
        run_save(videoname, 'pixel_per_um', loader.pixel_per_um)
        run_save(videoname, 'exposure_time', loader.exposure_time)
        run_save(videoname, 'statistics', None)
    return segmented


@segmentation_page.route('/set_segmentation_params/<path:videoname>/<runname>',
                         methods=['POST'])
def set_segmentation_params(videoname, runname):
    try:
        g.run = runname

        stored = run_load_multiple(videoname, ['config', 'pixel_per_um'])
        config = stored['config']
        pixel_per_um = stored['pixel_per_um']
        for key in ['segmentation_source', 'gauss_radius', 'threshold',
                    'segmentation_algorithm', 'spike_detection_algorithm',
                    'nSD_n']:
            config[key] = request.values.get(key, config[key])
        run_save(videoname, 'config', config)

        segmented = generate_segmentation(videoname, config)

        # Convert numpy arrays to flat lists
        response = {}
        response['segmentation'] = {}
        response['segmentation']['success'] = 'Segmentation generated'
        response['segmentation']['width'] = segmented['source'].shape[0]
        response['segmentation']['height'] = segmented['source'].shape[1]
        for k in segmented:
            response['segmentation'][k] = segmented[k].flatten().tolist()
        
        response['segmentation']['pixel_per_um'] = pixel_per_um
        response['config'] = config
        thresholds = analyzer.get_thresholds(segmented['filtered'])
        response['thresholds'] = thresholds
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/get_segmentation/<path:videoname>/<runname>')
def get_segmentation(videoname, runname):
    g.run = runname
    stored = run_load_multiple(videoname, ['segmentation', 'pixel_per_um',
                                           'config'])
    segmented = stored['segmentation']
    pixel_per_um = stored['pixel_per_um']
    config = stored['config']

    # Convert numpy arrays to flat lists
    response = {}
    response['segmentation'] = {}
    response['segmentation']['width'] = segmented['source'].shape[0]
    response['segmentation']['height'] = segmented['source'].shape[1]
    for k in segmented:
        response['segmentation'][k] = segmented[k].flatten().tolist()
    response['segmentation']['pixel_per_um'] = pixel_per_um
    response['config'] = config
    thresholds = analyzer.get_thresholds(segmented['filtered'])
    response['thresholds'] = thresholds

    return jsonify(response)


@segmentation_page.route('/create_run/<path:videoname>/<runname>',
                         methods=['POST'])
def create_run(videoname, runname):
    g.run = runname
    config = analyzer.util.get_default_config()

    run_save(videoname, 'config', config)
    generate_segmentation(videoname, config)

    return jsonify({'runs': list_runs(videoname)})


@segmentation_page.route('/delete_run/<path:videoname>/<runname>',
                         methods=['POST'])
def delete_run(videoname, runname):
    try:
        run_delete(videoname, runname)
        return jsonify({'runs': list_runs(videoname)})
    except Exception as e:
        return jsonify({'fail': str(e)})


@segmentation_page.route('/convert/<path:videoname>', methods=['POST'])
def convert(videoname):
    # We convert by opening the file
    analyzer.loader.open(
        os.path.join(current_app.config['VIDEO_FOLDER'], videoname))

    return jsonify({'success': True})


@segmentation_page.route('/get_runs/<path:videoname>')
def get_runs(videoname):
    if videoname.endswith('.tif'):
        return jsonify({'runs': list_runs(videoname)})
    elif videoname.endswith('.cxd'):
        return jsonify({'error': 'need_conversion'})
    else:
        return jsonify({'error': 'is_folder'})


@segmentation_page.route('/get_thresholds/<path:videoname>/<runname>')
def get_thresholds(videoname, runname):
    g.run = runname
    segmented = run_load(videoname, 'segmentation')
    thresholds = analyzer.get_thresholds(segmented['filtered'])
    return jsonify(**thresholds)


@segmentation_page.route('/get_config/<path:videoname>/<runname>')
def get_config(videoname, runname):
    g.run = runname
    config = run_load(videoname, 'config')
    return jsonify(config)


@segmentation_page.route('/get_borders/<path:videoname>/<runname>')
def get_borders(videoname, runname):
    g.run = runname
    segmented = run_load(videoname, 'segmentation')
    borders = segmented['borders'].flatten().tolist()
    return jsonify({'borders': borders})


@segmentation_page.route('/get_tree/')
def get_tree():
    return jsonify(make_tree(current_app.config['VIDEO_FOLDER']))


@segmentation_page.route('/')
@segmentation_page.route('/segmentation')
def main_page():
    files = listdir(current_app.config['VIDEO_FOLDER'])
    return render_template('main.html',
                           files=files)
