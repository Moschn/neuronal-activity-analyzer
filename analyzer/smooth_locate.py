from analyzer.locate import Locate
import numpy
import scipy.ndimage


class Smooth_locator(Locate):

    def __init__(self, smooth=5, threshold=0.05):
        self.smooth = smooth
        self.threshold = threshold

    def set_threshold(self, threshold):
	self.threshold = threshold

    def set_smooth(self, smooth):
	self.smooth = smooth

    def analyze_frame(self, frame):
        # copy numpy array, so it still stay intact for analysis
        img = numpy.copy(frame)

        # smooth the image
        if self.smooth > 0:
            self.img_smoothed = self._smooth(img, self.smooth)
	else:
	    self.img_smoothed = img

        # global threshold
        if self.threshold > 0:
            threshold = self._calcThreshold(img, self.threshold)
            self.img_thresholded = self.img_smoothed > threshold
        else:
            self.img_thresholded = self.img_smoothed

        # If wanted the cleaned image can be displayed
        # pyplot.imshow(img_thresholded,  cmap=cm.Greys_r)
        # pyplot.show()

        result = self._findNeurons(self.img_thresholded)

        return result

    def _calcThreshold(self, frame, percentage):
        color_range = numpy.amax(frame) - numpy.amin(frame)
        threshold = numpy.amin(frame) + percentage*color_range
        return threshold

    def _smooth(self, frame, radius):
        return scipy.ndimage.filters.gaussian_filter(
            frame, radius, mode='nearest')

    def _findNeurons(self, img):
        neuron_map = numpy.zeros(numpy.shape(img), dtype=numpy.int8)
        counter = 1
        while numpy.any(img):
            # Get one pixel belonging to a neuron and label its region
            indices = numpy.where(img)
            self._findRegion(
                img, neuron_map, indices[0][0], indices[1][0], counter)
            counter += 1
        print("Number of ROI: {}".format(counter-1))
        return neuron_map

    def _findRegion(self, img, target, x, y, label):
        """ Finds a region of True values in img, and writes index to all
        pixels of that area in target

        Args:
          img: Array to find ROIs in
          target: Array to write ROI to
          x, y: Starting point to fill the ROI
          label: Label of the ROI
        """

        pixels_to_check = [(x, y)]
        while pixels_to_check:
            index = pixels_to_check.pop()

            if (index[0] < 0 or
                    index[1] < 0 or
                    index[0] >= img.shape[0] or
                    index[1] >= img.shape[1]):
                continue
            if not img[index[0], index[1]]:
                continue

            img[index[0], index[1]] = False
            target[index[0], index[1]] = label

            pixels_to_check.append((index[0] - 1, index[1] - 1))
            pixels_to_check.append((index[0] - 1, index[1]))
            pixels_to_check.append((index[0] - 1, index[1] + 1))
            pixels_to_check.append((index[0], index[1] - 1))
            pixels_to_check.append((index[0], index[1] + 1))
            pixels_to_check.append((index[0] + 1, index[1] - 1))
            pixels_to_check.append((index[0] + 1, index[1]))
            pixels_to_check.append((index[0] + 1, index[1] + 1))
