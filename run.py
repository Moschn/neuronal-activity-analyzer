#!/usr/bin/env python

import analyzer
from matplotlib import pyplot


loader = analyzer.Loader.open('test/testfile.tif')
data = loader.next_frame()
print(data)
pyplot.figure(1)
pyplot.imshow(data, interpolation='nearest')
pyplot.show()
