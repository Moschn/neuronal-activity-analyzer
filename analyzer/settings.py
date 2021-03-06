THREAD_COUNT = 4

default_config = {
    'segmentation_source': 'mean',  # name of implementation
    'gauss_radius': 2.,             # sigma for gauss filter in pixels
    'threshold': 'li',              # float from 0 to 1 or name of algorithm
    'threshold_applicator': 'dynamicthreshold', # name of implementation
    'segmentation_algorithm': 'watershed',  # name of implementation
    'integrater': 'mean',           # name of implementation
    'spike_detection_algorithm': 'wdm',  # name of implementation
    'min_spike_width': 0.3,         # [s]
    'max_spike_width': 4,           # [s]
    'correlation_max_shift': 5.,    # [s]
    'nSD_n': 3.,                    # float, threshold value in standard
                                    # deviations for ntimesstd implementation
                                    # spike detection
}
