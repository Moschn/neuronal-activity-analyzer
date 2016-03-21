#!/usr/bin/python2

import wx
import numpy
from sys import argv
from analyzer.smooth_locate import Smooth_locator
from analyzer.integrator_sum import Integrator_sum

import analyzer


labelColors = [
    (0x00, 0x00, 0x00),
    (0xff, 0x00, 0x00),
    (0x00, 0xff, 0x00),
    (0xff, 0x00, 0x00),
    (0x00, 0xff, 0xff),
    (0xff, 0x00, 0xff),
    (0xff, 0xff, 0x00),
    (0x80, 0x00, 0x00),
    (0x00, 0x80, 0x00),
    (0x00, 0x00, 0x80),
    (0x00, 0x80, 0x80),
    (0x80, 0x00, 0x80),
    (0x80, 0x80, 0x00),
    (0x40, 0x00, 0x00),
    (0x00, 0x40, 0x00),
    (0x00, 0x00, 0x40),
    (0x00, 0x40, 0x40),
    (0x40, 0x00, 0x40),
    (0x40, 0x40, 0x00),
    (0xc0, 0x00, 0x00),
    (0x00, 0xc0, 0x00),
    (0x00, 0x00, 0xc0),
    (0x00, 0xc0, 0xc0),
    (0xc0, 0x00, 0xc0),
    (0xc0, 0xc0, 0x00)
]


def numpyToBitmap(img):
    """ Convert numpy RGB array to wxpython bitmap
    """
    image = wx.EmptyImage(img.shape[0], img.shape[1])
    image.SetData(img.tostring())
    wxBitmap = image.ConvertToBitmap()
    return wxBitmap    

def normalizeImage(img):
    brightness_max = numpy.amax(img)
    brightness_min = numpy.amin(img)    
    brightness_range = brightness_max - brightness_min
    return (img - brightness_min) / brightness_range * 255

def greyscale16ToNormRGB(img):
    # Convert to 8 bit
    img_f = numpy.array(img, dtype=numpy.float32)
    img_8 = numpy.array(normalizeImage(img_f), dtype=numpy.uint8)
    # Convert to RGB
    rgb = numpy.asarray(numpy.dstack((img_8, img_8, img_8)),
                        dtype=numpy.uint8)
    return rgb
    

def indexedToRGB(img, palette):
    """ Convert an array of color indices and a list of colors to a RGB image
    """
    rgb = numpy.zeros((img.shape[0], img.shape[1], 3), 'uint8')
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            rgb[y,x] = palette[img[y,x]]
    return rgb


class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Neural Activity Analyzer")

        self.CreateStatusBar()

        self.panel = wx.Panel(self)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        #
        # Image areas
        #

        self.imageAreaSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.imageAreaSizer)

        # Original image
        imageLabel = wx.StaticText(self.panel, label='Original frame')
        self.imageAreaSizer.Add(imageLabel)
        
        img = wx.EmptyImage(800, 600)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                         wx.BitmapFromImage(img))
        self.imageAreaSizer.Add(self.imageCtrl)

        # Smoothed image
        smoothedImageLabel = wx.StaticText(self.panel, label='Smoothed frame')
        self.imageAreaSizer.Add(smoothedImageLabel)
        self.smoothedImage = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                             wx.BitmapFromImage(img))
        self.imageAreaSizer.Add(self.smoothedImage)

        # Labeled image
        segmentedImageLabel = wx.StaticText(self.panel, label='Thresholded and segmented')
        self.imageAreaSizer.Add(segmentedImageLabel)
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
                                         value=50, minValue=0,
                                         maxValue=200, size=wx.Size(200,20))
        self.thresholdSliderBox.Add(self.thresholdSlider)
        self.controlSizer.Add(self.thresholdSliderBox)

        self.thresholdSlider.Bind(wx.EVT_SCROLL_CHANGED, self.onThresholdSliderScroll)

        #
        # gauss radius slider
        #
    
        self.gaussRadiusSliderBox = wx.BoxSizer(wx.HORIZONTAL)
        self.gaussRadiusSliderLabel = wx.StaticText(self.panel,
                                                  label='Gauss Radius')
        self.gaussRadiusSliderBox.Add(self.gaussRadiusSliderLabel)
        self.gaussRadiusSlider = wx.Slider(self.panel, wx.ID_ANY,
                                         value=5, minValue=1,
                                         maxValue=50, size=wx.Size(200,20))
        self.gaussRadiusSliderBox.Add(self.gaussRadiusSlider)
        self.controlSizer.Add(self.gaussRadiusSliderBox)
        self.gaussRadiusSlider.Bind(wx.EVT_SCROLL_CHANGED, self.onGaussRadiusSliderScroll)
        
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

        self.imageCtrl.SetBitmap(numpyToBitmap(greyscale16ToNormRGB(self.frame)))

        self.smoothedImage.SetBitmap(numpyToBitmap(greyscale16ToNormRGB(self.segmenter.img_smoothed)))

        labeledImage = numpy.mod(self.roi, len(labelColors))
        labeledBitmap = numpyToBitmap(indexedToRGB(labeledImage, labelColors))
        self.segmentedImage.SetBitmap(labeledBitmap)
        
    def setSegmenter(self, segmenter):
        self.segmenter = segmenter

    def setFile(self, path):
        self.path = path

        self.loader = analyzer.Loader.open(path)
        self.update()

    def onThresholdSliderScroll(self, event):
        threshold = float(event.GetPosition()) / 1000
        print threshold
        self.segmenter.set_threshold(threshold)
        self.update()

    def onGaussRadiusSliderScroll(self, event):
        self.segmenter.set_smooth(event.GetPosition())
        self.update()

app = wx.App(False)
frame = MainWindow(None)

if len(argv) > 1:
    frame.setFile(argv[1])

frame.Show(True)
app.MainLoop()
