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

t = WDM(1, 1)

plt.figure(1)
plt.subplot(411)
plt.plot(numpy.arange(0, 1, 1/12), t.wavelet_bior1_5(12))
plt.subplot(412)
plt.plot(numpy.arange(0, 1, 1/6), t.wavelet_bior1_5(6))
plt.subplot(413)
plt.plot(numpy.arange(0, 1, 1/18), t.wavelet_bior1_5(18))
plt.subplot(414)
plt.plot(numpy.arange(0, 1, 1/50), t.wavelet_bior1_5(50))
plt.show()


