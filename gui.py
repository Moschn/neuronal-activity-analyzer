#!/usr/bin/python2

import wx
from sys import argv

from ui.segmentation_window import SegmentationWindow
from ui.roi_editor import ROIEditor

from analyzer.defaults import default_config
from analyzer.util import apply_defaults

config = {
    'config_path': 'config.py'
}

# if 'config_path' in config:
#     try:
#         with open(config['config_path']) as config_file:
#             exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
#         except IOError as e:
#             print 'Unable to load configuration file (%s)' % e.strerror
#             raise

apply_defaults(config, default_config)

app = wx.App(False)

roi_editor = ROIEditor(None, None, config)
segmentation_window = SegmentationWindow(None, roi_editor, config)

segmentation_window.setFile(argv[1])

segmentation_window.Show(True)
app.MainLoop()

# save config
if 'config_path' in config:
    with open(config['config_path'], 'w') as f:
        for k, v in config.items():
            if type(v) == int:
                f.write("%s = %i\n" % (k, v))
            elif type(v) == float:
                f.write("%s = %f\n" % (k, v))
            elif type(v) == str:
                f.write("%s = '%s'\n" % (k, v))
            else:
                print("Not saving config value %s of type %s" % (k, type(v)))
