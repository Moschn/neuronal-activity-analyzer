from analyzer.integrater.integrater import Integrater
import numpy


class Mean(Integrater):

    def __init__(self, roi):
        self.roi = roi

    def process_frame(self, frame):
        activity = []  # list containing the brightness sum of each ROI
        for i in range(1, numpy.amax(self.roi)+1):
            region = self.roi == i
            activity.append(numpy.average(frame[region]))
        return numpy.array(activity)
