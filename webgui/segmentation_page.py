from os import listdir
import os
from threading import Lock

from flask import Blueprint, current_app, request, redirect, url_for
from flask import render_template, flash, send_file, jsonify, g
from werkzeug import secure_filename
from scipy.misc import imsave

import analyzer
from .util import check_extension, cache_load, cache_save, session_save
from .util import get_filename, list_sessions

segmentation_page = Blueprint('segmentation', __name__,
                              template_folder='templates')

# We use this lock to stop multiple requests arriving simultaniously from all
# calculating the segmentation. Just the first should calculate, the rest
# should get it from cache
segmentation_lock = Lock()


def get_segmentation(videoname, params):
    """ Run the segmentation in the analyzer module or get the result from
    cache.
    If running segmentation, store the result in cache and generate pngs of the
    intermediate steps, taged with segmentation_<image_type>
    The generated png files should have tags:
        segmentation_source
        segmentation_filtered
        segmentation_thresholded
        segmentation_segmented
    """
    with segmentation_lock:
        # If we have a cache result for that settings, use it
        cached = cache_load(videoname, params, 'segmentation')
        if cached:
            return cached

        loader = analyzer.loader.open(
            os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
        segmented = analyzer.segment(loader, params)
        cache_save(videoname, params, 'segmentation', segmented)

        # Save images to send to browser
        for k in segmented:
            filename = get_filename(videoname, params, 'segmentation_%s' % k,
                                    'png')
            imsave(filename, segmented[k])

    return segmented


@segmentation_page.route('/create_session/<videoname>/<sessionname>')
def create_session(videoname, sessionname):
    g.session = sessionname
    session_save(videoname, 'created', '')
    return jsonify({'sessions': list_sessions(videoname)})


@segmentation_page.route('/get_sessions/<videoname>')
def get_sessions(videoname):
    return jsonify({'sessions': list_sessions(videoname)})


@segmentation_page.route('/get_thresholds/<videoname>')
def get_thresholds(videoname):
    segmentation_params = {}
    for key in ['segmentation_source', 'gauss_radius',
                'threshold', 'segmentation_algorithm']:
        segmentation_params[key] = request.args.get(key)

    segmentation = get_segmentation(videoname, segmentation_params)

    thresholds = analyzer.get_thresholds(segmentation['filtered'])
    return jsonify(**thresholds)


@segmentation_page.route('/segmentation_image/<videoname>/<image_type>')
def segmentation_image(videoname, image_type):
    g.session = request.args.get('session')

    segmentation_params = {}
    for key in ['segmentation_source', 'gauss_radius',
                'threshold', 'segmentation_algorithm']:
        segmentation_params[key] = request.args.get(key)

    segmented = get_segmentation(videoname, segmentation_params)

    if request.args.get('save', '0') == '1':
        session_save(videoname, 'segmentation',
                     segmented['segmented'])
        session_save(videoname, 'displayable',
                     get_filename(videoname, segmentation_params,
                                  'segmentation_displayable', 'png'))

    path = get_filename(videoname, segmentation_params, image_type, 'png')
    return send_file(path, mimetype='image/png')


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
    return render_template('segmentation_page.html',
                           files=files)
