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


@statistics.route('/get_statistics/<path:videoname>/<run>')
def get_statistics(videoname, run):
    g.run = run

    response = run_load(videoname, 'statistics')
    if response is not None:
        return jsonify(**response)

    loader = analyzer.loader.open(
        os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
    segmentation = run_load(videoname, 'segmentation')
    config = run_load(videoname, 'config')
    
    integration_start = time.time()
    integrator = analyzer.integrator_sum.Integrator_sum(
        segmentation['editor'])
    activities = integrator.process_parallel_frames(loader)
    integration_time = time.time() - integration_start

    spike_detection_start = time.time()
    spikes = analyzer.detect_spikes(activities, config)
    spike_detection_time = time.time() - spike_detection_start
    fig_raster = analyzer.plot.plot_rasterplot(spikes, loader.exposure_time, 1)
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
    run_save(videoname, 'exposure_time', loader.exposure_time)

    return jsonify(**response)


@statistics.route('/get_statistics_rasterplot/<path:videoname>/<run>/<time_per_bin>')
def get_statistics_rasterplot(videoname, run, time_per_bin):
    g.run = run
    statistics = run_load(videoname, 'statistics')
    exposure_time = run_load(videoname, 'exposure_time')
    fig_raster = analyzer.plot.plot_rasterplot(statistics['spikes'],
                                               exposure_time,
                                               float(time_per_bin))
    response = {}
    response['rasterplot'] = mpld3.fig_to_dict(fig_raster)
    return jsonify(**response)
