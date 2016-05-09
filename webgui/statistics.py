from flask import Blueprint, g, current_app, jsonify
import os.path
import time
from math import floor

from .util import run_load, run_save
import analyzer
import analyzer.integrator_sum
import mpld3

statistics = Blueprint('statistics', __name__,
                       template_folder='templates')


@statistics.route('/get_statistics/<videoname>/<run>')
def get_statistics(videoname, run):
    g.run = run

    response = run_load(videoname, 'statistics')
    if response is not None:
        return jsonify(**response)

    loader = analyzer.loader.open(
        os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
    segmentation = run_load(videoname, 'segmentation')

    integration_start = time.time()
    integrator = analyzer.integrator_sum.Integrator_sum(
        segmentation['editor'])
    activities = integrator.process_parallel_frames(loader)
    integration_time = time.time() - integration_start

    spike_detection_start = time.time()
    spikes = analyzer.detect_spikes(activities,
                                    {'spike_detection_algorithm': 'wavelet'})
    spike_detection_time = time.time() - spike_detection_start
    fig_raster = analyzer.plot.plot_rasterplot(spikes, loader.exposure_time,
                                               floor(len(activities) *
                                                     loader.exposure_time))
    fig_roi = analyzer.plot.plot_roi(segmentation['editor'],
                                     segmentation['source'],
                                     loader.pixel_per_um)

    spikes = [l.tolist() for l in spikes]

    response = {}
    response['activities'] = activities.T.tolist()
    response['spikes'] = spikes

    response['time'] = {
        "activity_calculation": integration_time,
        "spike_detection": spike_detection_time
    }
    response['rasterplot'] = mpld3.fig_to_dict(fig_raster)
    response['roi'] = mpld3.fig_to_dict(fig_roi)

    run_save(videoname, 'statistics', response)

    return jsonify(**response)
