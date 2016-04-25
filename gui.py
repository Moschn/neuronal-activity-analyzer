#!/usr/bin/python2

import wx
from sys import argv

from ui.segmentation_window import SegmentationWindow
from ui.roi_editor import ROIEditor

from analyzer.util import apply_defaults, load_config, save_config


configpath = 'config.py'

config = load_config(configpath)

app = wx.App(False)

roi_editor = ROIEditor(None, None, config)
segmentation_window = SegmentationWindow(None, roi_editor, config)

segmentation_window.setFile(argv[1])

segmentation_window.Show(True)
app.MainLoop()

# save config
save_config(config, configpath)
