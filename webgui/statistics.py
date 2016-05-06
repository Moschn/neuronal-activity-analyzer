from flask import Blueprint, g, current_app, jsonify
import os.path
import time

from .util import run_load
import analyzer
import analyzer.integrator_sum

statistics = Blueprint('statistics', __name__,
                       template_folder='templates')


@statistics.route('/get_statistics/<videoname>/<run>')
def get_statistics(videoname, run):
    g.run = run

    loader = analyzer.loader.open(
        os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
    segmentation = run_load(videoname, 'segmentation')

    integration_start = time.time()
    integrator = analyzer.integrator_sum.Integrator_sum(
        segmentation['segmented'])
    activities = integrator.process_parallel_frames(loader)
    integration_time = time.time() - integration_start

    spike_detection_start = time.time()
    spikes = analyzer.detect_spikes(activities,
                                    {'spike_detection_algorithm': 'wavelet'})
    spike_detection_time = time.time() - spike_detection_start
    spikes = [l.tolist() for l in spikes]

    response = {}
    response['activities'] = activities.T.tolist()
    response['spikes'] = spikes

    response['time'] = {
        "activity_calculation": integration_time,
        "spike_detection": spike_detection_time
    }
    return jsonify(**response)
