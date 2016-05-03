from flask import Blueprint, g, current_app, jsonify
import os.path

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
    integrator = analyzer.integrator_sum.Integrator_sum(
        segmentation['segmented'])
    activities = integrator.process_parallel_frames(loader)

    spikes = analyzer.detect_spikes(activities,
                                    {'spike_detection_algorithm': 'wavelet'})
    spikes = [l.tolist() for l in spikes]

    response = {}
    response['activities'] = activities.T.tolist()
    response['spikes'] = spikes

    return jsonify(**response)
