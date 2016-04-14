#!/usr/bin/env python
import analyzer
import analyzer.filters
import analyzer.segmentation
from sys import argv
from matplotlib import pyplot
from matplotlib import gridspec
import matplotlib.cm as cm
import numpy


def _plot_segment(roi, ax):
    ax.imshow(roi)
    for i in range(1, int(numpy.amax(roi)+1)):
        coordinates_neuron = numpy.where(roi == i)
        ax.text(coordinates_neuron[1][0]+10,
                coordinates_neuron[0][0]+10, i, fontsize=20, color='white')


loader = analyzer.loader.open(argv[1])

frame = loader.next_frame()

frame_thresh_otsu = analyzer.filters.threshold_otsu(frame)

frame_thresh_li = analyzer.filters.threshold_li(frame)
frame_thresh_yen = analyzer.filters.threshold_yen(frame)

frame_gauss = analyzer.filters.gauss_filter(frame)

frame_thresh_otsu_gauss = analyzer.filters.threshold_otsu(frame_gauss)
frame_thresh_li_gauss = analyzer.filters.threshold_li(frame_gauss)
frame_thresh_yen_gauss = analyzer.filters.threshold_yen(frame_gauss)

label_thresh_otsu = analyzer.segmentation.label(frame_thresh_otsu)
label_thresh_li = analyzer.segmentation.label(frame_thresh_li)
label_thresh_yen = analyzer.segmentation.label(frame_thresh_yen)
label_thresh_otsu_gauss = analyzer.segmentation.label(frame_thresh_otsu_gauss)
label_thresh_li_gauss = analyzer.segmentation.label(frame_thresh_li_gauss)
label_thresh_yen_gauss = analyzer.segmentation.label(frame_thresh_yen_gauss)

watershed_thresh_otsu = analyzer.segmentation.watershed(frame_thresh_otsu)
watershed_thresh_li = analyzer.segmentation.watershed(frame_thresh_li)
watershed_thresh_yen = analyzer.segmentation.watershed(frame_thresh_yen)
watershed_thresh_otsu_gauss = analyzer.segmentation.watershed(frame_thresh_otsu_gauss)
watershed_thresh_li_gauss = analyzer.segmentation.watershed(frame_thresh_li_gauss)
watershed_thresh_yen_gauss = analyzer.segmentation.watershed(frame_thresh_yen_gauss)

try:
    rw_thresh_otsu = analyzer.segmentation.random_walker(frame_thresh_otsu)
except Exception as e:
    rw_thresh_otsu = numpy.zeros(numpy.shape(frame))
try:
    rw_thresh_li = analyzer.segmentation.random_walker(frame_thresh_li)
except Exception as e:
    rw_thresh_li = numpy.zeros(numpy.shape(frame))
try:
    rw_thresh_yen = analyzer.segmentation.random_walker(frame_thresh_yen)
except Exception as e:
    rw_thresh_yen = numpy.zeros(numpy.shape(frame))
try:
    rw_thresh_otsu_gauss = analyzer.segmentation.random_walker(frame_thresh_otsu_gauss)
except Exception as e:
    rw_thresh_otsu_gauss = numpy.zeros(numpy.shape(frame))
try:
    rw_thresh_li_gauss = analyzer.segmentation.random_walker(frame_thresh_li_gauss)
except Exception as e:
    rw_thresh_li_gauss = numpy.zeros(numpy.shape(frame))
try:
    rw_thresh_yen_gauss = analyzer.segmentation.random_walker(frame_thresh_yen_gauss)
except Exception as e:
    rw_thresh_yen_gauss = numpy.zeros(numpy.shape(frame))

x = 3
y = 8

grid = gridspec.GridSpec(x, y)


pyplot.figure(1)
ax = pyplot.subplot(grid[0, 0])
ax.imshow(frame_thresh_otsu, cmap=cm.Greys_r)
ax.set_title("otsu")
ax = pyplot.subplot(grid[0, 1])
ax.imshow(frame_thresh_otsu_gauss, cmap=cm.Greys_r)
ax.set_title("otsu gauss")
ax = pyplot.subplot(grid[1, 0])
ax.imshow(frame_thresh_li, cmap=cm.Greys_r)
ax.set_title("li")
ax = pyplot.subplot(grid[1, 1])
ax.imshow(frame_thresh_li_gauss, cmap=cm.Greys_r)
ax.set_title("li gauss")
ax = pyplot.subplot(grid[2, 0])
ax.imshow(frame_thresh_yen, cmap=cm.Greys_r)
ax.set_title("yen")
ax = pyplot.subplot(grid[2, 1])
ax.imshow(frame_thresh_yen_gauss, cmap=cm.Greys_r)
ax.set_title("yen gauss")

ax = pyplot.subplot(grid[0, 2])
_plot_segment(label_thresh_otsu, ax)
ax.set_title("label: otsu")
ax = pyplot.subplot(grid[0, 3])
_plot_segment(label_thresh_otsu_gauss, ax)
ax.set_title("label: otsu gauss")
ax = pyplot.subplot(grid[1, 2])
_plot_segment(label_thresh_li, ax)
ax.set_title("label: li")
ax = pyplot.subplot(grid[1, 3])
_plot_segment(label_thresh_li_gauss, ax)
ax.set_title("label: li gauss")
ax = pyplot.subplot(grid[2, 2])
_plot_segment(label_thresh_yen, ax)
ax.set_title("label: yen")
ax = pyplot.subplot(grid[2, 3])
_plot_segment(label_thresh_yen_gauss, ax)
ax.set_title("label: yen gauss")

ax = pyplot.subplot(grid[0, 4])
_plot_segment(watershed_thresh_otsu, ax)
ax.set_title("watershed: otsu")
ax = pyplot.subplot(grid[0, 5])
_plot_segment(watershed_thresh_otsu_gauss, ax)
ax.set_title("watershed: otsu gauss")
ax = pyplot.subplot(grid[1, 4])
_plot_segment(watershed_thresh_li, ax)
ax.set_title("watershed: li")
ax = pyplot.subplot(grid[1, 5])
_plot_segment(watershed_thresh_li_gauss, ax)
ax.set_title("watershed: li gauss")
ax = pyplot.subplot(grid[2, 4])
_plot_segment(watershed_thresh_yen, ax)
ax.set_title("watershed: yen")
ax = pyplot.subplot(grid[2, 5])
_plot_segment(watershed_thresh_yen_gauss, ax)
ax.set_title("watershed: yen gauss")

ax = pyplot.subplot(grid[0, 6])
_plot_segment(rw_thresh_otsu, ax)
ax.set_title("rw: otsu")
ax = pyplot.subplot(grid[0, 7])
_plot_segment(rw_thresh_otsu_gauss, ax)
ax.set_title("rw: otsu gauss")
ax = pyplot.subplot(grid[1, 6])
_plot_segment(rw_thresh_li, ax)
ax.set_title("rw: li")
ax = pyplot.subplot(grid[1, 7])
_plot_segment(rw_thresh_li_gauss, ax)
ax.set_title("rw: li gauss")
ax = pyplot.subplot(grid[2, 6])
_plot_segment(rw_thresh_yen, ax)
ax.set_title("rw: yen")
ax = pyplot.subplot(grid[2, 7])
_plot_segment(rw_thresh_yen_gauss, ax)
ax.set_title("rw: yen gauss")

pyplot.show()