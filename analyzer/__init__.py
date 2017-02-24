import analyzer.loader.loader
from analyzer.loader.loader import Loader
import analyzer.plot
import analyzer.util
import analyzer.apply_threshold
import analyzer.apply_threshold.apply_threshold
import analyzer.segmentation
import analyzer.segmentation.segmentation
import analyzer.threshold
import analyzer.threshold.threshold
import analyzer.spike_detection
import analyzer.spike_detection.spike_detection
import analyzer.integrater
import analyzer.integrater.integrater
import analyzer
import os
import csv
import numpy

thresholding_algorithms = analyzer.util.list_implementations(
    analyzer.threshold, analyzer.threshold.threshold.Threshold)


Loader.find_loader_class()  # all sublasses of loader get registered in loader


def get_thresholds(image):
    """ Returns a dictionary of the li, otsu and yen thresholds for an image
    """
    result = {}
    for k, v in thresholding_algorithms.items():
        thresholder = v()
        result[k.lower()] = thresholder.get_threshold(image)
    return result


def open_video(videoname):
    return analyzer.loader.loader.open(videoname)


def segment(loader, config):
    """ Using a loader and a config do filtering, thresholding and segmentation
    """
    # copy config, to not change external representation
    config = config.copy()

    # Convert gauss sigma parameter
    config['gauss_radius'] = float(config['gauss_radius'])

    # Get source image
    if config['segmentation_source'] == 'first_frame':
        source = loader.get_frame(0)
    elif config['segmentation_source'] == 'mean':
        source = loader.get_mean()
    elif config['segmentation_source'] == 'variance':
        source = loader.get_variance()
    else:
        print("Config error, unknown source method selected")
        print("Falling back to the mean of all frames")
        source = loader.get_mean()

    # Apply gaussian filter
    filtered = analyzer.threshold.threshold.Threshold.gaussian_filter(
        source, config['gauss_radius'])

    # Parse threshold parameter
    try:
         config['threshold'] = float(config['threshold'])
    except ValueError:
        config['threshold'] = get_thresholds(filtered)[config['threshold']]

    # Apply threshold
    threshold_applicator = analyzer.util.find_impl(
        analyzer.apply_threshold, analyzer.apply_threshold.apply_threshold.ApplyThreshold,
        config['threshold_applicator'])
    thresholded = threshold_applicator().apply_threshold(loader, filtered, config['threshold'])

    # Apply segmentation algorithm
    segmentation_class = analyzer.util.find_impl(
        analyzer.segmentation, analyzer.segmentation.segmentation.Segmentation,
        config['segmentation_algorithm'])
    segmentor = segmentation_class()
    segmented = segmentor.get_segmentation(thresholded)

    # return borders as well
    borders = analyzer.threshold.threshold.Threshold.get_borders(segmented)

    return {
        'source': source,
        'filtered': filtered,
        'thresholded': thresholded,
        'segmented': segmented,
        'borders': borders,
    }


def calculate_activities(loader, segmented, config):
    integrater_class = analyzer.util.find_impl(
        analyzer.integrater,
        analyzer.integrater.integrater.Integrater,
        config['integrater'])

    integrater = integrater_class(segmented)
    return integrater.process_parallel_frames(loader)


def detect_spikes(activity, config, exposure_time):
    sd_class = analyzer.util.find_impl(
        analyzer.spike_detection,
        analyzer.spike_detection.spike_detection.SpikeDetection,
        config['spike_detection_algorithm'])

    spike_detector = sd_class(config, exposure_time)

    return spike_detector.detect_spikes_parallel(activity)


def save_results(roi, frame, pixel_per_um, exposure_time, activities, spikes,
                 time_per_bin, correlation,  videoname, analysis_folder):
    if not os.path.exists(analysis_folder):
        os.makedirs(analysis_folder)

    activities = numpy.array(activities)

    analyzer.plot.save_roi(roi, frame, pixel_per_um,
                           videoname, analysis_folder)

    fig_raster = analyzer.plot.plot_rasterplot(spikes,
                                               exposure_time,
                                               float(time_per_bin))
    analyzer.plot.save(fig_raster, os.path.join(analysis_folder,
                                                'rasterplot.svg'))

    with open(os.path.join(analysis_folder, 'activity.csv'), 'w') as csvfile:
        writer = csv.writer(csvfile)
        for neuron_activity in activities:
            writer.writerow(neuron_activity)

    total_spikes = 0

    summary_peaks = []
    with open(os.path.join(analysis_folder, 'activity_spikes.csv'),
              'w') as csvfile:
        writer = csv.writer(csvfile)
        idx = 1
        for maxima_time in spikes:
            neuron_activity = activities[idx-1]
            fname = os.path.join(analysis_folder, 'neuron_plots',
                                 'neuron_{}.svg'.format(idx))
            if not os.path.exists(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))
            fig = analyzer.plot.plot_spikes(neuron_activity, maxima_time)
            analyzer.plot.save(fig, fname)

            writer.writerow(maxima_time)

            peaks_time = round(len(maxima_time) /
                               (exposure_time*len(activities.T)),
                               4)
            total_spikes += len(maxima_time)
            summary_peaks.append("Neuron {}: \t{} peaks/s".format(idx,
                                                                  peaks_time))
            idx += 1

    # plot correlations
    fig_correlation = analyzer.plot.plot_correlation_heatmap(correlation)
    analyzer.plot.save(fig_correlation, os.path.join(analysis_folder,
                                                     'correlations.svg'))

    with open(os.path.join(analysis_folder, 'summary.txt'), 'w') as summary:
        summary.write("Summary of analysis of {}\n".format(videoname))
        summary.write("Number of neurons found: {}\n".format(numpy.max(roi)))
        for line in summary_peaks:
            summary.write(line + "\n")
        peaks_time = total_spikes/(exposure_time *
                                   len(activities.T))/numpy.max(roi)
        summary.write("Total number of spikes per second per neuron: {}".
                      format(peaks_time))
