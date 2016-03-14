#!/usr/bin/env python
import analyzer
from matplotlib import pyplot
import matplotlib.cm as cm
from analyzer.smooth_locate import Smooth_locator
from analyzer.integrator_sum import Integrator_sum

from PIL import Image
import numpy

loader = analyzer.Loader.open('test/testfile.tif')

frame = loader.next_frame()

segment = Smooth_locator()
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

print(activities)

for neuron_activity in activities.T:
    pyplot.plot(neuron_activity)

pyplot.show()

print(activities)

pyplot.figure(1)
pyplot.subplot(211)
pyplot.imshow(frame,  cmap=cm.Greys_r)
pyplot.subplot(212)
pyplot.imshow(roi,  cmap=cm.Greys_r)
pyplot.show()
