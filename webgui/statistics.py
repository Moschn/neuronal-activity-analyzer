from flask import Blueprint, g, current_app, jsonify
import os.path
import time

from .util import run_save, run_load_multiple
import analyzer
import analyzer.integrator_sum
from analyzer.normalize import normalize
from analyzer.correlation import correlate_activities
import mpld3


statistics = Blueprint('statistics', __name__,
                       template_folder='templates')


@statistics.route('/get_statistics/<path:videoname>/<run>')
def get_statistics(videoname, run):
    try:
        g.run = run

        stored = run_load_multiple(videoname, ['statistics', 'segmentation',
                                               'config', 'exposure_time'])
        response = stored['statistics']
        segmentation = stored['segmentation']
        config = stored['config']
        exposure_time = stored['exposure_time']

        if response is not None:
            return jsonify(**response)

        loader = analyzer.loader.open(
            os.path.join(current_app.config['VIDEO_FOLDER'], videoname))

        integration_start = time.time()
        integrator = analyzer.integrator_sum.Integrator_sum(
            segmentation['editor'])
        activities = integrator.process_parallel_frames(loader)
        activities = normalize(activities)
        integration_time = time.time() - integration_start

        spike_detection_start = time.time()
        spikes = analyzer.detect_spikes(activities, config, exposure_time)
        spike_detection_time = time.time() - spike_detection_start

        correlations_start = time.time()
        correlations = correlate_activities(activities, exposure_time)
        correlation_time = time.time() - correlations_start

        fig_raster = analyzer.plot.plot_rasterplot(spikes,
                                                   exposure_time,
                                                   1)
        fig_roi = analyzer.plot.plot_roi(segmentation['editor'],
                                         segmentation['source'],
                                         loader.pixel_per_um)
        run_save(videoname, 'time_per_bin', 1)

        spikes = [l.tolist() for l in spikes]
        correlations = [l.tolist() for l in correlations]

        response = {}
        response['activities'] = activities.tolist()
        response['spikes'] = spikes
        response['correlations'] = correlations

        response['time'] = {
            "activity_calculation": integration_time,
            "spike_detection": spike_detection_time,
            "correlation": correlation_time
        }
        response['rasterplot'] = mpld3.fig_to_dict(fig_raster)
        response['roi'] = mpld3.fig_to_dict(fig_roi)
        response['exposure_time'] = exposure_time

        response['success'] = True
        run_save(videoname, 'statistics', response)
        run_save(videoname, 'exposure_time', loader.exposure_time)

        return jsonify(**response)
    except Exception as e:
        raise
        return jsonify(fail=str(e))


@statistics.route(
    '/get_statistics_rasterplot/<path:videoname>/<run>/<time_per_bin>')
def get_statistics_rasterplot(videoname, run, time_per_bin):
    g.run = run
    stored = run_load_multiple(videoname, ['statistics', 'exposure_time'])
    statistics = stored['statistics']
    exposure_time = stored['exposure_time']
    fig_raster = analyzer.plot.plot_rasterplot(statistics['spikes'],
                                               exposure_time,
                                               float(time_per_bin))
    run_save(videoname, 'time_per_bin', time_per_bin)
    response = {}
    response['rasterplot'] = mpld3.fig_to_dict(fig_raster)
    return jsonify(**response)


@statistics.route('/save_plots/<path:videoname>/<run>', methods=['POST'])
def save_plots(videoname, run):
    g.run = run
    analysis_folder = os.path.join(current_app.config['VIDEO_FOLDER'],
                                   os.path.dirname(videoname),
                                   os.path.basename(videoname) + "-analysis")
    stored = run_load_multiple(videoname, ['segmentation', 'pixel_per_um',
                                           'time_per_bin', 'statistics',
                                           'exposure_time'])
    segmentation = stored['segmentation']
    pixel_per_um = stored['pixel_per_um']

    time_per_bin = stored['time_per_bin']
    statistics = stored['statistics']
    exposure_time = stored['exposure_time']

    analyzer.save_results(segmentation['editor'], segmentation['source'],
                          pixel_per_um, exposure_time,
                          statistics['activities'], statistics['spikes'],
                          time_per_bin, os.path.basename(videoname),
                          analysis_folder)
    response = {'done': True}
    return jsonify(response)
