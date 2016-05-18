from analyzer.loader import register_loader_class
import analyzer.pillow_loader
import analyzer.bioformat_loader
from analyzer.wdm import WDM
from analyzer.nsd_spike import SD_spike_detection
import analyzer.segmentation
import analyzer.plot
import analyzer.util
import os
import csv
import numpy

register_loader_class(analyzer.pillow_loader.PILLoader)
register_loader_class(analyzer.bioformat_loader.BioFormatLoader)


def get_thresholds(image):
    """ Returns a dictionary of the li, otsu and yen thresholds for an image
    """
    return {
        'li':   analyzer.segmentation.li_thresh_relative(image),
        'otsu': analyzer.segmentation.otsu_thresh_relative(image),
        'yen':  analyzer.segmentation.yen_thresh_relative(image)
    }


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
    filtered = analyzer.segmentation.\
        gaussian_filter(source, config['gauss_radius'])

    # Parse threshold parameter
    if config['threshold'] in ['li', 'otsu', 'yen']:
        config['threshold'] = get_thresholds(filtered)[config['threshold']]
    config['threshold'] = float(config['threshold'])

    # Apply threshold
    thresholded = analyzer.segmentation.\
        threshold(filtered, config['threshold'])

    # Apply segmentation algorithm
    if config['segmentation_algorithm'] == 'watershed':
        segmented = analyzer.segmentation.watershed(thresholded)
    elif config['segmentation_algorithm'] == 'randomwalk':
        segmented = analyzer.segmentation.\
                         random_walker(thresholded)
    elif config['segmentation_algorithm'] == 'kmeans':
        segmented = analyzer.segmentation.k_means(thresholded)
    elif config['segmentation_algorithm'] == 'fill':
        segmented = analyzer.segmentation.label(thresholded)
    else:
        print("Config error, unknown segmentation alogrithm selected")
        print("Falling back to the watershed algorithm")
        segmented = analyzer.segmentation.watershed(thresholded)

    # return borders as well
    borders = analyzer.segmentation.get_borders(segmented)

    return {
        'source': source,
        'filtered': filtered,
        'thresholded': thresholded,
        'borders': borders,
        'segmented': segmented,
    }


def detect_spikes(activity, config):
    if config['spike_detection_algorithm'] == 'wavelet':
        algo = WDM(50, 700)  # TODO: adaptive min/max spike width
        spikes = algo.detect_spikes_parallel(activity)
    elif config['spike_detection_algorithm'] == 'nSD':
        if 'nSD_n' in config:
            n = config['nSD_n']
        else:
            print("""If the n*SD spike detection method is
            selected an additional 'nSD_n' parameter is required""")
            print("A n value of 1 is assumed")
            n = 1
        algo = SD_spike_detection(n)
        spikes = algo.detect_spikes_parallel(activity)
    else:
        print("Config error, unknown spike detection alogrithm selected")
        print("Falling back to the wavelet detection method")
        algo = WDM(50, 700)  # TODO: adaptive min/max spike width
        spikes = algo.detect_spikes_parallel(activity)

    return spikes


def save_results(roi, frame, pixel_per_um, exposure_time, activities, spikes,
                 time_per_bin, videoname, analysis_folder):
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

    with open(os.path.join(analysis_folder, 'summary.txt'), 'w') as summary:
        summary.write("Summary of analysis of {}\n".format(videoname))
        summary.write("Number of neurons found: {}\n".format(numpy.max(roi)))
        for line in summary_peaks:
            summary.write(line + "\n")
        peaks_time = total_spikes/(exposure_time *
                                   len(activities.T))/numpy.max(roi)
        summary.write("Total number of spikes per second per neuron: {}".
                      format(peaks_time))
