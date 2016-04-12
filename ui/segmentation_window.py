import wx
import numpy

from ui.image_conv import *
import analyzer.segmentation

sourceMethods = ['first_frame', 'mean', 'variance']
separationMethods = ['watershed', 'randomwalk', 'kmeans', 'correlation']

class SegmentationWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent,
                          title="Neural Activity Analyzer - Segmentation")

        self.panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        self.sizer = wx.GridSizer(cols=2, rows=2, vgap=10, hgap=10)

        # Empty image if no file is loaded
        emptyImage = wx.EmptyImage(400, 400)
        
        #
        # First step: Select source image for segmentation
        #
        self.sourceSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sourceImage = wx.StaticBitmap(self.panel, bitmap=wx.BitmapFromImage(emptyImage),
                                           size=wx.Size(400,400))
        self.sourceSizer.Add(self.sourceImage, 1, wx.SHAPED)

        self.sourceMethodSizer = wx.BoxSizer(wx.VERTICAL)
        self.sourceMethodChooser = wx.RadioBox(self.panel, choices=sourceMethods,
                                               size=wx.Size(200, 60),
                                               style=wx.VERTICAL)
        self.sourceMethodChooser.Bind(wx.EVT_RADIOBOX, self.onSourceMethodChanged)
        self.sourceMethodSizer.Add(self.sourceMethodChooser)
        self.sourceSizer.Add(self.sourceMethodSizer)
        
        self.sizer.Add(self.sourceSizer, 1, wx.EXPAND)

        #
        # Second step: Gauss filtering
        #

        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.filteredImage = wx.StaticBitmap(self.panel, bitmap=wx.BitmapFromImage(emptyImage),
                                             size=wx.Size(400, 400))
        self.filterSizer.Add(self.filteredImage, 1, wx.SHAPED)

        self.filterControlSizer = wx.GridSizer(cols=2)
        self.gaussRadiusSliderLabel = wx.StaticText(self.panel,
                                                  label='Gauss Radius')
        self.gaussRadiusSlider = wx.Slider(self.panel, value=20, minValue=0,
                                            maxValue=50, size=wx.Size(200, 20))
        self.gaussRadiusSlider.SetTickFreq(5)
        self.gaussRadiusSlider.Bind(wx.EVT_SCROLL_CHANGED, self.onGaussRadiusChanged)
        self.filterControlSizer.Add(self.gaussRadiusSliderLabel)
        self.filterControlSizer.Add(self.gaussRadiusSlider)
        self.filterSizer.Add(self.filterControlSizer)

        self.sizer.Add(self.filterSizer, 1, wx.EXPAND)

        #
        # Third step: Thresholding
        #
        
        self.thresholdingSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.thresholdedImage = wx.StaticBitmap(self.panel, bitmap=wx.BitmapFromImage(emptyImage))
        self.thresholdingSizer.Add(self.thresholdedImage)

        self.thresholdingControlSizer = wx.GridSizer(cols=2)
        self.thresholdSliderLabel = wx.StaticText(self.panel,
                                                  label='Threshold')
        self.thresholdSlider = wx.Slider(self.panel, value=50, minValue=0,
                                         maxValue=200, size=wx.Size(200,20))
        self.thresholdSlider.Bind(wx.EVT_SCROLL_CHANGED, self.onThresholdChanged)
        self.thresholdingControlSizer.Add(self.thresholdSliderLabel)
        self.thresholdingControlSizer.Add(self.thresholdSlider)
        self.thresholdingSizer.Add(self.thresholdingControlSizer)

        self.sizer.Add(self.thresholdingSizer, 1, wx.EXPAND)

        #
        # Fourth step: Separation
        #

        self.separationSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.separatedImage = wx.StaticBitmap(self.panel, bitmap=wx.BitmapFromImage(emptyImage))
        self.separationSizer.Add(self.separatedImage)

        self.separationMethodSizer = wx.BoxSizer(wx.VERTICAL)
        self.separationMethodChooser = wx.RadioBox(self.panel,
                                                   choices=separationMethods,
                                                   style=wx.VERTICAL)
        self.separationMethodChooser.Bind(wx.EVT_RADIOBOX, self.onSeparationMethodChanged)
        self.separationMethodSizer.Add(self.separationMethodChooser)
        self.separationSizer.Add(self.separationMethodSizer)

        self.sizer.Add(self.separationSizer, 1, wx.EXPAND)
        
        #
        # finalize window
        #
        
        self.panel.SetSizer(self.sizer)
        self.panel.Fit()
        self.SetAutoLayout(True)
        self.Layout()

        #
        # Init segmenter parameters
        #

        self.sourceMethod = sourceMethods[0]
        self.gaussRadius = 20
        self.threshold = 0.05
        self.separationMethod = separationMethods[0]

        self.update()

    def update(self):
        if not hasattr(self, 'loader'):
            return

        if 'first_frame' in self.sourceMethod:
            source = self.loader.get_frame(0)
        elif 'mean' in self.sourceMethod:
            source = self.loader.get_mean()
        elif 'variance' in self.sourceMethod:
            source = self.loader.get_variance()
        else:
            print("Error, no source method selected")
            return

        self.sourceImage.SetBitmap(numpyToBitmap(greyscale16ToNormRGB(source)))
        
        filtered = analyzer.segmentation.gaussian_filter(source, self.gaussRadius)

        self.filteredImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(filtered)))


        thresholded = analyzer.segmentation.threshold(filtered, self.threshold)

        self.thresholdedImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(thresholded)))

        if self.separationMethod == 'watershed':
            segmented = analyzer.segmentation.watershed(thresholded)
        elif self.separationMethod == 'randomwalk':
            segmented = analyzer.segmentation.random_walker(thresholded)
        elif self.separationMethod == 'kmeans':
            segmented = analyzer.segmentation.k_means(thresholded)

        self.separatedImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(segmented)))
        
        self.sizer.Fit(self)

    def setSegmenter(self, segmenter):
        self.segmenter = segmenter

    def setFile(self, path):
        self.path = path

        self.loader = analyzer.loader.open(path)

        frame = self.loader.get_frame(0)
        self.sourceImage.SetSize(wx.Size(frame.shape[0], frame.shape[1]))
        self.filteredImage.SetSize(wx.Size(frame.shape[0], frame.shape[1]))
        self.thresholdedImage.SetSize(wx.Size(frame.shape[0], frame.shape[1]))
        self.separatedImage.SetSize(wx.Size(frame.shape[0], frame.shape[1]))
        
        self.update()

    def onSourceMethodChanged(self, event):
        self.sourceMethod = event.GetString()
        self.update()

    def onSeparationMethodChanged(self, event):
        self.separationMethod = event.GetString()
        self.update()

    def onThresholdChanged(self, event):
        threshold = float(event.GetPosition()) / 1000
        self.threshold = threshold
        self.update()

    def onGaussRadiusChanged(self, event):
        self.gaussRadius = event.GetPosition()
        self.update()
