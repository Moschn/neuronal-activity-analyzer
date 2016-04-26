from analyzer.loader import Loader, register_loader_class
import analyzer.pillow_loader
import analyzer.bioformat_loader

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
        print("Error, no source method selected")
        return

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

    return {
        'source': source,
        'filtered': filtered,
        'thresholded': thresholded,
        'segmented': segmented
    }
