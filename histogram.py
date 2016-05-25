#!/usr/bin/env python3
import analyzer.util
import analyzer
import analyzer.segmentation
import analyzer.plot
from sys import argv
import numpy
from matplotlib import pyplot


def plot_histogram(source, thresholds=[]):
    pyplot.style.use('ggplot')

    col1 = pyplot.rcParams['axes.color_cycle'][1]
    col2 = pyplot.rcParams['axes.color_cycle'][0]

    fig = pyplot.figure()
    ax = pyplot.gca()
    n, bins, patches = ax.hist(source.ravel(), 128, color=col1)
    ax.set_yscale('log')
    ax.vlines(thresholds, 0, max(n), color=col2, label=['li', 'otsu', 'yen'],
              linewidth=4.0)
    ax.set_autoscale_on(False)
    pyplot.axis([0, 256, 0, 10**5])
    ax.set_xlabel("Greyscale", fontsize=36)
    ax.set_ylabel("Number of pixels", fontsize=36)
    ax.tick_params(axis='both', which='major', labelsize=28)
    ax.tick_params(axis='both', which='minor', labelsize=28)
    pyplot.tight_layout()
    return fig


config = analyzer.util.load_config('config.py')
lo = analyzer.loader.open(argv[1])
segmentation = analyzer.segment(lo, config)
source = segmentation['filtered']

range = numpy.amax(source)-numpy.amin(source)
source = (source-numpy.amin(source))/range*255

thresholds = analyzer.get_thresholds(source)
threshold_abs = []

print(numpy.amax(source) - numpy.amin(source))
for k, t in thresholds.items():
    print(t)
    threshold_abs.append(numpy.amin(source) + t *
                         (numpy.amax(source) - numpy.amin(source)))


fig = plot_histogram(source, threshold_abs)
pyplot.show()
