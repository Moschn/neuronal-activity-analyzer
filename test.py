#!/usr/bin/python
import matplotlib.pyplot as plt
from matplotlib import gridspec
import analyzer
import numpy
import scipy.ndimage
from skimage import data
from skimage.filters import threshold_otsu, threshold_adaptive
from skimage.filters import threshold_isodata, threshold_li, threshold_yen
from analyzer.wdm import WDM

t = WDM(60, 350)

plt.figure(1)
plt.subplot(411)
plt.plot(numpy.arange(0, 1, 1/150), t.wavelet_ricker(150))
plt.subplot(412)
plt.plot(numpy.arange(0, 1, 1/70), t.wavelet_ricker(70))
plt.subplot(413)
plt.plot(numpy.arange(0, 1, 1/80), t.wavelet_ricker(80))
plt.subplot(414)
plt.plot(numpy.arange(0, 1, 1/250), t.wavelet_ricker(250))
plt.show()
