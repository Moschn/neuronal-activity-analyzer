#!/usr/bin/env python
import numpy
import analyzer
import analyzer.filters
import analyzer.segmentation
from analyzer.wdm import WDM
import os
from sys import argv
from analyzer.integrator_sum import Integrator_sum
import csv
from matplotlib import pyplot
from matplotlib import gridspec
import time

time_frame=0.03

def analyze_file(filename, directory):
    start_time = time.clock()
    print("analyzing file {}/{}".format(directory, filename))
    loader = analyzer.loader.open("{}/{}".format(directory, filename))
    frame = loader.next_frame()

    print("\tfilter and threshold...")
    #frame = analyzer.filters.gauss_filter(frame, 3)
    frame_thresh = analyzer.filters.threshold_otsu(frame)

    print("\tfinding neurons...")
    roi = analyzer.segmentation.watershed(frame_thresh)

    sum_roi = Integrator_sum(roi)
    print("\tanalyzing all frames...")
    activities = sum_roi.process_parallel_frames(loader)

    print("\tploting results...")
    fig = pyplot.figure()
    pyplot.imshow(roi)
    for i in range(1, numpy.amax(roi)+1):
        coordinates_neuron = numpy.where(roi == i)
        pyplot.text(coordinates_neuron[1][0]+10,
                    coordinates_neuron[0][0]+10, i, fontsize=20, color='white')
    pyplot.savefig('{}/{}_roi.png'.format(root, filename), bbox_inches='tight')
    pyplot.close(fig)

    with open('{}/{}_activity.csv'.format(root, filename), 'w') as csvfile:
        writer = csv.writer(csvfile)
        for neuron_activity in activities.T:
            writer.writerow(neuron_activity)

    print("\tdetecting spikes...")
    summary_peaks = []

    spike_det = WDM(50, 500)
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
            fig = pyplot.figure()
            pyplot.subplot(211)
            pyplot.plot(neuron_activity)
            time_filled = numpy.zeros(len(neuron_activity))
            for t in maxima_time:
                time_filled[t] = 1
            pyplot.subplot(212)
            pyplot.plot(time_filled)
            pyplot.savefig('{}/{}_neuron_{}.png'.format(root, filename, idx),
                           bbox_inches='tight')
            pyplot.close(fig)
            writer.writerow(maxima_time)

            peaks_time = len(maxima_time)/(time_frame*len(activities.T))
            total_spikes += len(maxima_time)
            summary_peaks.append("Neuron {}: \t{} peaks/s".format(idx, peaks_time))
            idx += 1
            
    with open('{}/{}_summary.txt'.format(directory, filename), 'w') as summary:
        summary.write("Summary of analysis of {}\n".format(filename))
        summary.write("Number of neurons found: {}\n".format(numpy.max(roi)))
        for line in summary_peaks:
            summary.write(line + "\n")
        peaks_time = total_spikes/(time_frame*len(activities.T))/numpy.max(roi)
        summary.write("Total number of spikes per second per neuron: {}".format(peaks_time))
        elapsed_time = time.clock() - start_time
        
        summary.write("\ntime used for analysis: {}".format(elapsed_time))

path = argv[1]
for root, dirs, files in os.walk(path):
    for name in files:
        if os.stat('{}/{}'.format(root, name)).st_size > 100000000:
            analyze_file(name, root)
