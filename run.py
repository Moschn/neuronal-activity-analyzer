#!/usr/bin/env python
import analyzer
from matplotlib import pyplot
import matplotlib.cm as cm
from analyzer.smooth_locate import Smooth_locator

from PIL import Image
import numpy

loader = analyzer.Loader.open('test/testfile.tif')

data = loader.next_frame()


print(data)

segment = Smooth_locator()
result = segment.analyze_frame(data)


pyplot.figure(1)
pyplot.subplot(211)
pyplot.imshow(data,  cmap=cm.Greys_r)
pyplot.subplot(212)
pyplot.imshow(result,  cmap=cm.Greys_r)
pyplot.show()
