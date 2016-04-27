#!/usr/bin/env python
import numpy
import analyzer
import analyzer.filters
import analyzer.segmentation
import analyzer.util
import analyzer.plot
from analyzer.wdm import WDM
import os
from sys import argv
from analyzer.integrator_sum import Integrator_sum
import csv
from matplotlib import pyplot
from matplotlib import gridspec
from matplotlib import cm
from skimage import segmentation
import time

# shutter time in s
time_frame = 0.03


def analyze_file(filename, directory):
    start_time = time.clock()
    print("analyzing file {}/{}".format(directory, filename))
    loader = analyzer.loader.open("{}/{}".format(directory, filename))
    frame = loader.next_frame()

    print("\tfilter and threshold...")
    frame = analyzer.filters.gauss_filter(frame, 3)
    frame_thresh = analyzer.filters.threshold_otsu(frame)

    print("\tfinding neurons...")
    roi = analyzer.segmentation.watershed(frame_thresh)

    sum_roi = Integrator_sum(roi)
    print("\tanalyzing all frames...")
    activities = sum_roi.process_parallel_frames(loader)

    print("\tploting results...")
    
    # plot roi
    improved_roi = False
    files = [f for f in os.listdir(directory) if
             os.path.isfile(os.path.join(directory, f))]
    for f in files:
        fn = os.path.join(directory, f)
        if f.endswith(".tif") and os.stat(fn).st_size < 100000000:
            try:
                loader2 = analyzer.loader.open(fn)
                fg_frame = loader2.get_frame(0)
                bg_frame = loader2.get_frame(1)

                figure = analyzer.plot.plot_roi_bg(roi, bg_frame, fg_frame)
                fname = '{}/{}_roi_improved.svg'.format(root, filename)
                analyzer.plot.save(figure, fname)
                improved_roi = True
                
            except Exception as e:
                print("No seperate imagefile with background/foreground found.")
                print("Only basic plot of ROIs will be generated!")
                
                pass
    if not improved_roi:
        fname = '{}/{}_roi.png'.format(root, filename)
        fig = analyzer.plot.plot_roi(roi, frame)
        analyzer.plot.save(fig, fname)
                
    with open('{}/{}_activity.csv'.format(root, filename), 'w') as csvfile:
        writer = csv.writer(csvfile)
        for neuron_activity in activities.T:
            writer.writerow(neuron_activity)

    print("\tdetecting spikes...")
    summary_peaks = []

    spike_det = WDM(50, 700)
    spikes = spike_det.detect_spikes_parallel(activities)
    print("\tplotting results...")

    total_spikes = 0
    
    with open('{}/{}_activity_spikes.csv'.format(root, filename), 'w') as csvfile:
        writer = csv.writer(csvfile)
        idx = 1
        for maxima_time in spikes:
            #spike_det = WDM(40, 150)
            #(maxima, maxima_time) = spike_det.detect_spikes(neuron_activity)
            neuron_activity = activities.T[idx-1]
            fname = '{}/{}_neuron_{}.svg'.format(root, filename, idx)
            fig = analyzer.plot.plot_spikes(neuron_activity, maxima_time)
            analyzer.plot.save(fig, fname)
            
            writer.writerow(maxima_time)

            peaks_time = len(maxima_time)/(time_frame*len(activities.T))
            total_spikes += len(maxima_time)
            summary_peaks.append("Neuron {}: \t{} peaks/s".format(idx, peaks_time))
            idx += 1

    # plot rasterplot
    fname = '{}/{}_rasterplot.svg'.format(root, filename)
    fig = analyzer.plot.plot_rasterplot(spikes, time_frame, 40)
    analyzer.plot.save(fig, fname)
            
    with open('{}/{}_summary.txt'.format(directory, filename), 'w') as summary:
        summary.write("Summary of analysis of {}\n".format(filename))
        summary.write("Number of neurons found: {}\n".format(numpy.max(roi)))
        for line in summary_peaks:
            summary.write(line + "\n")
        peaks_time = total_spikes/(time_frame*len(activities.T))/numpy.max(roi)
        summary.write("Total number of spikes per second per neuron: {}".format(peaks_time))
        elapsed_time = time.clock() - start_time
        
        summary.write("\ntime used for analysis: {}".format(elapsed_time))


config = analyzer.util.load_config('config.py')
        
path = argv[1]
for root, dirs, files in os.walk(path):
    for name in files:
        if os.stat('{}/{}'.format(root, name)).st_size > 100000000:
            analyze_file(name, root)
