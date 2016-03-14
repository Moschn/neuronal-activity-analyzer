from analyzer.integrator import Integrator
import numpy

from matplotlib import pyplot
import matplotlib.cm as cm

class Integrator_sum(Integrator):

    def __init__(self, roi):
        self.roi = roi
        self.sizes = numpy.bincount(self.roi.flatten())

    def process_frame(self, frame):
        activity = [] # list containing the brightness sum of each ROI
        for i in range(1, numpy.amax(self.roi)+1):
            region = self.roi == i
            activity.append(frame[region].sum()/self.sizes[i])
        return numpy.array(activity)
