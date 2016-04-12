#!/usr/bin/python2

import wx
from sys import argv

from ui.segmentation_window import SegmentationWindow


app = wx.App(False)
frame = SegmentationWindow(None)

if len(argv) > 1:
    frame.setFile(argv[1])

frame.Show(True)
app.MainLoop()
