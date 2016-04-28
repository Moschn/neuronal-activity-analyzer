from analyzer.loader import Loader, register_loader_class
import analyzer.pillow_loader
import analyzer.bioformat_loader
from analyzer.wdm import WDM
from analyzer.nsd_spike import SD_spike_detection

register_loader_class(analyzer.pillow_loader.PILLoader)
register_loader_class(analyzer.bioformat_loader.BioFormatLoader)


def segment(loader, config):
    """ Using a loader and a config do filtering, thresholding and segmentation
    """
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

    filtered = analyzer.segmentation.\
        gaussian_filter(source, config['gauss_radius'])

    # if no threshold is set yet, set one now (li)
    if 'threshold' not in config:
        config['threshold'] = analyzer.segmentation.\
                                   li_thresh_relative(filtered)

    thresholded = analyzer.segmentation.\
        threshold(filtered, config['threshold'])

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

    return {
        'source': source,
        'filtered': filtered,
        'thresholded': thresholded,
        'segmented': segmented
    }

def detect_spikes(activity, config):
    if config['spike_detection_algorithm'] == 'wavelet':
        algo = WDM(50, 700)  # TODO: adaptive min/max spike width
        spikes = algo.detect_spikes_parallel(activity)
    elif config['spike_detection_algorithm'] == 'nSD':
        if 'nSD_n' in config:
            n = config['nSD_n']
        else:
            print("If the n*SD spike detection method is ", end="")
            print("selected an additional 'nSD_n' parameter is required")
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
