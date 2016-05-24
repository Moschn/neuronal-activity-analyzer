import analyzer
import analyzer.filters
import analyzer.segmentation
import analyzer.util
import analyzer.plot
import os
from analyzer.integrator_sum import Integrator_sum


def analyze_file(filename, directory, config):
    videoname = os.path.join(directory, filename)
    analysis_folder = os.path.join(directory, filename + "-analysis")

    print("analyzing file {}/{}".format(directory, filename))
    loader = analyzer.loader.open(videoname)
    time_frame = loader.exposure_time
    pixel_per_um = loader.pixel_per_um

    print("\tfinding neurons...")
    segmented = analyzer.segment(loader, config)
    roi = segmented['segmented']
    frame = segmented['source']

    sum_roi = Integrator_sum(roi)
    print("\tanalyzing all frames...")
    activities = sum_roi.process_parallel_frames(loader)

    print("\tdetecting spikes...")
    summary_peaks = []

    spikes = analyzer.detect_spikes(activities, config, time_frame)
    print("\tplotting results...")

    analyzer.save_results(roi, frame, pixel_per_um, time_frame,
                          activities.T, spikes, 1, videoname, analysis_folder)


def analyze_all_in_folder(path, config):
    for root, dirs, files in os.walk(path):
        for name in files:
            if os.stat('{}/{}'.format(root, name)).st_size > 100000000:
                analyze_file(name, root, config)
