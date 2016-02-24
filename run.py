#!/usr/bin/env python
import analyzer
from matplotlib import pyplot
import matplotlib.cm as cm

loader = analyzer.Loader.open('test/testfile.tif')
data = loader.next_frame()
print(data)
print(data.shape)
# pyplot.figure(1)
pyplot.imshow(data,  cmap=cm.Greys_r)
pyplot.show()
