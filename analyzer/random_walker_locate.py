from analyzer.locate import Locate
import numpy
import scipy.ndimage
import skimage
from skimage.feature import peak_local_max
from matplotlib import pyplot


class Random_walker_locate(Locate):

    def __init__(self, random_walker=1, threshold=1):
        self.random_walker = random_walker
        self.threshold = threshold
        pass

    def analyze_frame(self, frame):
        # copy numpy array, so it still stay intact for analysis
        img = numpy.copy(frame)

        img = scipy.ndimage.filters.gaussian_filter(img, 1)
        # li threshold
        if self.threshold > 0:
            threshold = skimage.filters.threshold_li(img)
            img = img > threshold

        # random walker
        if self.random_walker > 0:
            result = self._random_walker(img)

        # If wanted the cleaned image can be displayed
        pyplot.imshow(result)
        pyplot.show()

        # result = self._findNeurons(img_thresholded)

        return result

    def _calcThreshold(self, frame, percentage):
        color_range = numpy.amax(frame) - numpy.amin(frame)
        threshold = numpy.amin(frame) + percentage*color_range
        return threshold

    def _smooth(self, frame, radius):
        return scipy.ndimage.filters.gaussian_filter(
            frame, radius, mode='nearest')

    def _random_walker(self, frame):
        # from http://www.scipy-lectures.org/packages/scikit-image/
        distance = scipy.ndimage.distance_transform_edt(frame)
        # print(distance)
        local_maxi = peak_local_max(distance, indices=False,
                                    footprint=numpy.ones((10, 10)),
                                    labels=frame)
        # print(local_maxi)
        markers = skimage.morphology.label(local_maxi)
        # markers = scipy.ndimage.label(local_maxi)[0]

        from skimage import segmentation
        # Transform markers image so that 0-valued pixels are to
        # be labelled, and -1-valued pixels represent background
        markers[~frame] = -1
        return segmentation.random_walker(frame, markers)

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
