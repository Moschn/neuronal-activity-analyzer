THREAD_COUNT = 4

CORRELATION_MAX_SHIFT = 5.  # maximum time shift to calculate correlation [s]

# Min spike width in seconds for wavelet method
MIN_SPIKE_WIDTH = 0.3
MAX_SPIKE_WIDTH = 4

default_config = {
    'segmentation_source': 'mean',
    'gauss_radius': 2,
    'threshold': 'li',
    'segmentation_algorithm': 'watershed',
    'spike_detection_algorithm': 'wdm',
    'nSD_n': 3,
    'integrater': 'mean',
}
