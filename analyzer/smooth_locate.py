from analyzer.locate import Locate
import numpy
import scipy.ndimage

from matplotlib import pyplot
import matplotlib.cm as cm


class Smooth_locator(Locate):

    def __init__(self):
        pass

    def analyze_frame(self, frame):
        # copy numpy array, so it still stay intact for analysis
        img = numpy.copy(frame)

        # smooth the image
        img = self.smooth(img, 5)
        # threshold to cut off all connections between neurons
        threshold = self.calcThreshold(img, 0.05)
        self.threshold(img, threshold)

        # If wanted the cleaned image can be displayed
        # pyplot.imshow(img,  cmap=cm.Greys_r)
        # pyplot.show()

        # Flood fill algorithm for finding the connected spots (neurons)
        threshold = self.calcThreshold(img, 0.05)
        result = self.findNeurons(img, threshold)

        return result

    def calcThreshold(self, frame, percent):
        threshold = numpy.amax(frame) - numpy.amin(frame)
        threshold = numpy.amin(frame) + threshold*percent
        return threshold

    def smooth(self, frame, radius):
        return scipy.ndimage.filters.gaussian_filter(
            frame, radius, mode='nearest')

    def threshold(self, frame, threshold):
        lowIndices = frame < threshold
        frame[lowIndices] = 0
        return frame

    def countNeurons(self, frame, threshold):
        img = numpy.copy(frame)
        counter = 0
        l = []
        while(numpy.any(img > threshold)):
            highindices = numpy.where(img > numpy.amax(img)-10)
            l.append((highindices[0][0], highindices[1][0]))
            self.forkDestroy(
                img, highindices[0][0], highindices[1][0], threshold)
            counter += 1
            print(counter)
            # pyplot.imshow(img,  cmap=cm.Greys_r)
            # pyplot.show()

        for (x, y) in l:
            img[x, y] = 0xffff
            print((x, y))
        return counter

    def findNeurons(self, img, threshold):
        result = numpy.zeros(numpy.shape(img), dtype=numpy.int8)
        counter = 1
        l = []
        while(numpy.any(img > threshold)):
            highindices = numpy.where(img > numpy.amax(img)-10)
            l.append((highindices[0][0], highindices[1][0]))
            self.forkCount(
                img, highindices[0][0], highindices[1][0], threshold,
                result, counter)
            counter += 1
        print("Number of ROI: {}".format(counter-1))
        return result

    def forkDestroy(self, frame, x, y, threshold):
        """ This function deletes the current pixel and then calls itself width
        all neighbour white pixels """
        # print(frame[max(0, x-1):x+2, max(y-1, 0):y+2])
        if not numpy.any(frame[max(0, x-1):x+2, max(0, y-1):y+2]) > 0:
            return
        for x2 in range(max(0, x-2), min(x+3, frame.shape[0])):
            for y2 in range(max(0, y-2), min(y+3, frame.shape[1])):
                frame[x2][y2] = 0
        for x2 in range(max(0, x-3), min(x+4, frame.shape[0]), 3):
            for y2 in range(max(0, y-3), min(y+4, frame.shape[1]), 3):
                if frame[x2][y2] > threshold:
                    self.forkDestroy(frame, x2, y2, threshold)

    def forkCount(self, frame, x, y, threshold, result, counter):
        """ This function sets the counter at the current pixel in the result
        arrayand then calls itself with all neighbour pixels above the
        threshold """
        # print(frame[max(0, x-1):x+2, max(y-1, 0):y+2])
        if not numpy.any(frame[max(0, x-1):x+2, max(0, y-1):y+2]) > 0:
            return
        for x2 in range(max(0, x-2), min(x+3, frame.shape[0])):
            for y2 in range(max(0, y-2), min(y+3, frame.shape[1])):
                frame[x2][y2] = 0
                result[x2][y2] = counter
        for x2 in range(max(0, x-3), min(x+4, frame.shape[0]), 3):
            for y2 in range(max(0, y-3), min(y+4, frame.shape[1]), 3):
                if frame[x2][y2] > threshold:
                    self.forkCount(frame, x2, y2, threshold, result, counter)
