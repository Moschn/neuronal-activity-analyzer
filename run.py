#!/usr/bin/env python
import numpy
import analyzer
from matplotlib import pyplot
from matplotlib import gridspec
import matplotlib.cm as cm
# from analyzer.smooth_locate import Smooth_locator
from analyzer.watershed_locate import Watershed_locate
from analyzer.integrator_sum import Integrator_sum

loader = analyzer.Loader.open('test/testfile.tif')

frame = loader.next_frame()/1000

# avarage first 50 frames
for i in range(1, 1000):
    frame += loader.next_frame()/1000

loader = analyzer.Loader.open('test/testfile.tif')

segment = Watershed_locate(1, 1)
roi = segment.analyze_frame(frame)

sum_roi = Integrator_sum(roi)
frame_activity = sum_roi.process_frame(frame)
activities = numpy.array(frame_activity)

frame_counter = 1
while True:
    try:
        print(frame_counter)
        frame_counter += 1
        frame = loader.next_frame()
        activities = numpy.vstack((activities, sum_roi.process_frame(frame)))
        # activities.append(sum_roi.process_frame(frame))
    except EOFError:
        print('finished')
        break

grid = gridspec.GridSpec(2, 2)

pyplot.figure(1)
pyplot.subplot(grid[0, 0])
pyplot.imshow(frame,  cmap=cm.Greys_r)
pyplot.subplot(grid[0, 1])
pyplot.imshow(roi)
for i in range(1, numpy.amax(roi)+1):
    coordinates_neuron = numpy.where(roi == i)
    pyplot.text(coordinates_neuron[1][0]+10,
                coordinates_neuron[0][0]+10, i, fontsize=20, color='white')
pyplot.subplot(grid[1, :])
neuron_nr = 1
for neuron_activity in activities.T:
    pyplot.plot(neuron_activity, label='neuron {}'.format(neuron_nr))
    neuron_nr += 1
pyplot.legend()
pyplot.show()
