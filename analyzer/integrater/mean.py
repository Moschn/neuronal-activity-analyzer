from analyzer.integrater.integrater import Integrater
import numpy


class Mean(Integrater):

    def __init__(self, segmented):
        super().__init__(segmented)
        self.roi_arr = numpy.zeros((numpy.amax(segmented), segmented.shape[0],
                                    segmented.shape[1]), dtype='bool')
        for i in range(1, numpy.amax(segmented)+1):
            self.roi_arr[i-1] = segmented == i

    def process_frame(self, frame):
        activity = []  # list containing the brightness sum of each ROI
        for segmented in self.roi_arr:
            activity.append(numpy.average(frame[segmented]))
        return numpy.array(activity)
