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
    frame_activity = sum_roi.process_frame(frame)
    activities = numpy.array(frame_activity)

    print("\tanalyzing all frames...")
    frame_counter = 1
    while True:
        try:
            frame_counter += 1
            frame = loader.next_frame()
            activities = numpy.vstack((activities, sum_roi.process_frame(frame)))
            # activities.append(sum_roi.process_frame(frame))
        except EOFError:
            break

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
    with open('{}/{}_activity_spikes.csv'.format(root, filename), 'w') as csvfile:
        writer = csv.writer(csvfile)
        idx = 1
        for neuron_activity in activities.T:
            spike_det = WDM(40, 150)
            (maxima, maxima_time) = spike_det.detect_spikes(neuron_activity)
            fig = pyplot.figure()
            pyplot.subplot(311)
            pyplot.plot(neuron_activity)
            pyplot.subplot(312)
            pyplot.plot(maxima)
            time_filled = numpy.zeros(len(maxima))
            for t in maxima_time:
                time_filled[t] = 1
            pyplot.subplot(313)
            pyplot.plot(time_filled)
            pyplot.savefig('{}/{}_neuron_{}.png'.format(root, filename, idx),
                           bbox_inches='tight')
            pyplot.close(fig)
            writer.writerow(maxima_time)
            summary_peaks.append("Neuron {}: \t{} peaks".format(idx, len(maxima_time)))
            idx += 1
            
    with open('{}/{}_summary.txt'.format(directory, filename), 'w') as summary:
        summary.write("Summary of analysis of {}\n".format(filename))
        summary.write("Number of neurons found: {}\n".format(numpy.max(roi)))
        for line in summary_peaks:
            summary.write(line + "\n")
        elapsed_time = time.clock() - start_time
        summary.write("\ntime used for analysis: {}".format(elapsed_time))

        
    
path = argv[1]
for root, dirs, files in os.walk(path):
    for name in files:
        if os.stat('{}/{}'.format(root, name)).st_size > 100000000:
            analyze_file(name, root)

