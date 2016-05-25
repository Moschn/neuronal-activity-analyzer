#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib import gridspec
import analyzer
import numpy
import scipy.ndimage
from skimage import data
from skimage.filters import threshold_otsu, threshold_adaptive
from skimage.filters import threshold_isodata, threshold_li, threshold_yen
from sys import argv

loader = analyzer.loader.open(argv[1])

image = loader.next_frame()
image = loader.get_mean()

image = image.astype('int64')

image = scipy.ndimage.filters.gaussian_filter(
            image, 3, mode='nearest')

image = loader.get_mean()

global_thresh = threshold_otsu(image)
binary_global = image > global_thresh

block_size = 99
binary_adaptive = threshold_adaptive(image, block_size, offset=10)

thresh_isodata = threshold_isodata(image)
binary_isodata = image > thresh_isodata

thresh_li = threshold_li(image)
binary_li = image > thresh_li

thresh_yen = threshold_yen(image)
binary_yen = image > thresh_yen

color_range = numpy.amax(image) - numpy.amin(image)
thresh_manual = numpy.amin(image) + 0.11*color_range
binary_manual = image > thresh_manual

grid = gridspec.GridSpec(3, 3)

# fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(7, 8))
# ax0, ax1, ax2, ax3, ax4 = axes
plt.gray()

fig = plt.subplot(grid[0, 0])
plt.imshow(image)
fig.set_title('Image')

fig = plt.subplot(grid[1, 0])
plt.imshow(binary_global)
fig.set_title('Global thresholding')

fig = plt.subplot(grid[2, 0])
plt.imshow(binary_adaptive)
fig.set_title('Adaptive thresholding')

fig = plt.subplot(grid[0, 1])
plt.imshow(binary_isodata)
fig.set_title('threshold isodata')

fig = plt.subplot(grid[1, 1])
plt.imshow(binary_li)
fig.set_title('threshold li')

fig = plt.subplot(grid[2, 1])
plt.imshow(binary_yen)
fig.set_title('threshold yen')

fig = plt.subplot(grid[0, 2])
plt.imshow(binary_manual)
fig.set_title('threshold manual')

plt.show()
