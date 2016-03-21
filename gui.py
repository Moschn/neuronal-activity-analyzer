#!/usr/bin/python2

import wx
import numpy
from sys import argv
from analyzer.smooth_locate import Smooth_locator
from analyzer.integrator_sum import Integrator_sum

import analyzer


def numpyToBitmap(numpy_img):
    # Convert to 8 bit
    img_8 = numpy_img # fail
    # Convert to RGB
    rgb = numpy.asarray(numpy.dstack((img_8, img_8, img_8)),
                        dtype=numpy.uint8)
    
    image = wx.EmptyImage(numpy_img.shape[0], numpy_img.shape[1])
    image.SetData(rgb.tostring())
    wxBitmap = image.ConvertToBitmap()
    return wxBitmap


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Neural Activity Analyzer")

        self.CreateStatusBar()

        self.panel = wx.Panel(self)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        #
        # Image area
        #

        self.imageAreaSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.imageAreaSizer)
        
        img = wx.EmptyImage(800, 600)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                         wx.BitmapFromImage(img))
        self.imageAreaSizer.Add(self.imageCtrl)

        self.segmentedImage = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                              wx.BitmapFromImage(img))
        self.imageAreaSizer.Add(self.segmentedImage)

        #
        # Begin of controls
        #
        
        self.controlSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.controlSizer)

        #
        # threshold slider
        #
        
        self.thresholdSliderBox = wx.BoxSizer(wx.HORIZONTAL)
        self.thresholdSliderLabel = wx.StaticText(self.panel,
                                                  label='Threshold')
        self.thresholdSliderBox.Add(self.thresholdSliderLabel)
        self.thresholdSlider = wx.Slider(self.panel, wx.ID_ANY,
                                         value=0.1, minValue=0,
                                         maxValue=1, size=wx.Size(200,20))
        self.thresholdSliderBox.Add(self.thresholdSlider)
        self.controlSizer.Add(self.thresholdSliderBox)

        self.thresholdSlider.Bind(wx.EVT_SCROLL, self.onThresholdSliderScroll)

        #
        # gauss radius slider
        #
    
        self.gaussRadiusSliderBox = wx.BoxSizer(wx.HORIZONTAL)
        self.gaussRadiusSliderLabel = wx.StaticText(self.panel,
                                                  label='Gauss Radius')
        self.gaussRadiusSliderBox.Add(self.gaussRadiusSliderLabel)
        self.gaussRadiusSlider = wx.Slider(self.panel, wx.ID_ANY,
                                         value=0.1, minValue=0,
                                         maxValue=1, size=wx.Size(200,20))
        self.gaussRadiusSliderBox.Add(self.gaussRadiusSlider)
        self.controlSizer.Add(self.gaussRadiusSliderBox)

        #
        # finalize window
        #
        
        self.panel.SetSizer(self.sizer)
        self.panel.SetAutoLayout(True)
        self.sizer.Fit(self)

        self.panel.Layout()

        self.setSegmenter(Smooth_locator())
        self.frame_index = 0

    def update(self):
        if not self.loader:
            return
        
        self.frame = self.loader.get_frame(self.frame_index)
        self.roi = self.segmenter.analyze_frame(self.frame)

        self.imageCtrl.SetBitmap(numpyToBitmap(self.frame))

    def setSegmenter(self, segmenter):
        self.segmenter = segmenter

    def setFile(self, path):
        self.path = path

        self.loader = analyzer.Loader.open(path)
        self.update()

    def onThresholdSliderScroll(self, event):
        self.threshold = event.GetPosition()
        self.update()

app = wx.App(False)
frame = MainWindow(None)

if len(argv) > 1:
    frame.setFile(argv[1])

frame.Show(True)
app.MainLoop()
