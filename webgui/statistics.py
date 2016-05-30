from flask import Blueprint, current_app, jsonify, request
import os.path
import time
import traceback

from .runs import Run
import analyzer
from analyzer.normalize import normalize
from analyzer.correlation import correlate_activities
import mpld3


statistics_blueprint = Blueprint('statistics', __name__,
                                 template_folder='templates')


@statistics_blueprint.route('/get_statistics/<path:videoname>/<runname>')
def get_statistics(videoname, runname):
    try:
        with Run(videoname, runname) as run:
            # If there is a cached response, use it
            response = run['statistics']
            if response is not None:
                return jsonify(**response)

            segmentation = run['segmentation']
            config = run['config']
            exposure_time = run['exposure_time']

        # Load the file
        loader = analyzer.open_video(
            os.path.join(current_app.config['VIDEO_FOLDER'], videoname))

        # Calculate the activities
        integration_start = time.time()
        activities = analyzer.calculate_activities(
            loader, segmentation['editor'], config)
        activities = normalize(activities)
        integration_time = time.time() - integration_start

        # Detect spikes in the activities
        spike_detection_start = time.time()
        spikes = analyzer.detect_spikes(activities, config, exposure_time)
        spike_detection_time = time.time() - spike_detection_start

        # Calculate correlation functions
        correlations_start = time.time()
        correlations = correlate_activities(activities, config, exposure_time)
        correlation_time = time.time() - correlations_start

        # Generate the rasterplot of the spikes
        fig_raster = analyzer.plot.plot_rasterplot(spikes,
                                                   exposure_time,
                                                   1)
        # Generate the figure with rois
        fig_roi = analyzer.plot.plot_roi(segmentation['editor'],
                                         segmentation['source'],
                                         loader.pixel_per_um)

        # Build response
        response = {}
        response['activities'] = activities.tolist()
        response['spikes'] = [l.tolist() for l in spikes]
        response['correlations'] = [l.tolist() for l in correlations]
        response['exposure_time'] = exposure_time

        response['rasterplot'] = mpld3.fig_to_dict(fig_raster)
        response['roi'] = mpld3.fig_to_dict(fig_roi)

        response['time'] = {
            "activity_calculation": integration_time,
            "spike_detection": spike_detection_time,
            "correlation": correlation_time
        }

        response['success'] = True

        with Run(videoname, runname) as run:
            # Save to cache and send response
            run['statistics'] = response
            # Set initial binsize to 1
            run['time_per_bin'] = 1

        return jsonify(**response)
    except Exception:
        return jsonify(fail=traceback.format_exc())


@statistics_blueprint.route(
    '/get_statistics_rasterplot/<path:videoname>/<runname>',
    methods=['POST'])
def get_statistics_rasterplot(videoname, runname):
    with Run(videoname, runname) as run:
        run['time_per_bin'] = float(request.form['time_per_bin'])

        fig_raster = analyzer.plot.plot_rasterplot(run['statistics']['spikes'],
                                                   run['exposure_time'],
                                                   run['time_per_bin'])
    rasterplot = mpld3.fig_to_dict(fig_raster)
    return jsonify(rasterplot=rasterplot)


@statistics_blueprint.route(
    '/save_plots/<path:videoname>/<runname>', methods=['POST'])
def save_plots(videoname, runname):
    analysis_folder = os.path.join(current_app.config['VIDEO_FOLDER'],
                                   "%s-analysis" % videoname)

    with Run(videoname, runname) as run:
        segmentation_editor = run['segmentation']['editor']
        segmentation_source = run['segmentation']['source']
        pixel_per_um = run['pixel_per_um']
        exposure_time = run['exposure_time']
        activities = run['statistics']['activities']
        spikes = run['statistics']['spikes']
        time_per_bin = run['time_per_bin']
        correlations = run['statistics']['correlations']

    analyzer.save_results(segmentation_editor,
                          segmentation_source,
                          pixel_per_um,
                          exposure_time,
                          activities,
                          spikes,
                          time_per_bin,
                          correlations,
                          os.path.basename(videoname),
                          analysis_folder)

    return jsonify(done=True)
