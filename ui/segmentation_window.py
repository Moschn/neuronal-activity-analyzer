import wx

from ui.image_conv import numpyToBitmap
from analyzer.util import greyscale16ToNormRGB
import analyzer.segmentation

source_methods = ['first_frame', 'mean', 'variance']
separation_methods = ['watershed',
                      'randomwalk',
                      'kmeans',
                      'fill',
                      'correlation']


class SegmentationWindow(wx.Frame):
    def __init__(self, parent, nextFrame, config):
        wx.Frame.__init__(self, parent,
                          title="Neural Activity Analyzer - Segmentation")

        self.nextFrame = nextFrame
        self.config = config

        self.panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        self.gridSizer = wx.GridSizer(cols=2, rows=2, vgap=10, hgap=10)

        self._createWindows()

    def _createWindows(self):
        # Empty image if no file is loaded
        emptyImage = wx.EmptyImage(800, 800)

        #
        # First step: Select source image for segmentation
        #
        self.sourceImage = wx.StaticBitmap(
            self.panel,
            bitmap=wx.BitmapFromImage(emptyImage),
            size=wx.Size(400, 400))
        self.sourceMethodChooser = wx.RadioBox(self.panel,
                                               choices=source_methods,
                                               style=wx.VERTICAL)
        self.sourceMethodChooser.Bind(wx.EVT_RADIOBOX,
                                      self.onSourceMethodChanged)

        self.sourceSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sourceSizer.Add(self.sourceImage, 1, wx.SHAPED | wx.ALL)
        self.sourceControlSizer = wx.BoxSizer(wx.VERTICAL)
        self.sourceControlSizer.Add(self.sourceMethodChooser,
                                    0, wx.EXPAND | wx.ALL)
        self.sourceSizer.Add(self.sourceControlSizer, 0, wx.EXPAND | wx.ALL)
        self.gridSizer.Add(self.sourceSizer, 1, wx.EXPAND)

        #
        # Second step: Gauss filtering
        #

        self.filterSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.filteredImage = wx.StaticBitmap(
            self.panel,
            bitmap=wx.BitmapFromImage(emptyImage),
            size=wx.Size(400, 400))
        self.filterSizer.Add(self.filteredImage, 1, wx.SHAPED)

        self.filterControlSizer = wx.GridSizer(cols=2)
        self.gaussRadiusSliderLabel = wx.StaticText(self.panel,
                                                    label='Gauss Radius')
        self.gaussRadiusSlider = wx.Slider(self.panel, value=20, minValue=0,
                                           maxValue=50, size=wx.Size(200, 20))
        self.gaussRadiusSlider.SetTickFreq(5)
        self.gaussRadiusSlider.Bind(wx.EVT_SCROLL_CHANGED,
                                    self.onGaussRadiusChanged)
        self.filterControlSizer.Add(self.gaussRadiusSliderLabel, 0,
                                    wx.FIXED_MINSIZE | wx.ALIGN_LEFT)
        self.filterControlSizer.Add(self.gaussRadiusSlider, 1, wx.EXPAND)
        self.filterSizer.Add(self.filterControlSizer, 0, wx.ALIGN_TOP)

        self.gridSizer.Add(self.filterSizer, 1, wx.EXPAND)

        #
        # Third step: Thresholding
        #

        self.thresholdingSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.thresholdedImage = wx.StaticBitmap(
            self.panel, bitmap=wx.BitmapFromImage(emptyImage))
        self.thresholdingSizer.Add(self.thresholdedImage, 1, wx.SHAPED)

        self.thresholdingControlSizer = wx.GridSizer(cols=2)
        self.thresholdSliderLabel = wx.StaticText(self.panel,
                                                  label='Threshold')
        self.thresholdSlider = wx.Slider(self.panel, value=50, minValue=0,
                                         maxValue=200, size=wx.Size(200, 40))
        self.thresholdSlider.Bind(wx.EVT_SCROLL_CHANGED,
                                  self.onThresholdChanged)
        self.thresholdingControlSizer.Add(self.thresholdSliderLabel,
                                          0, wx.ALIGN_LEFT)
        self.thresholdingControlSizer.Add(self.thresholdSlider,
                                          0, wx.EXPAND)

        self.liButton = wx.Button(self.panel, -1, 'Li',
                                  size=wx.Size(200, 40))
        self.otsuButton = wx.Button(self.panel, -1, 'Otsu',
                                    size=wx.Size(200, 40))
        self.yenButton = wx.Button(self.panel, -1, 'Yen',
                                   size=wx.Size(200, 40))
        self.thresholdingControlSizer.Add(self.liButton)
        self.thresholdingControlSizer.Add(self.otsuButton)
        self.thresholdingControlSizer.Add(self.yenButton)
        self.liButton.Bind(wx.EVT_BUTTON, self.onLiButtonClicked)
        self.otsuButton.Bind(wx.EVT_BUTTON, self.onOtsuButtonClicked)
        self.yenButton.Bind(wx.EVT_BUTTON, self.onYenButtonClicked)

        self.thresholdingSizer.Add(self.thresholdingControlSizer,
                                   0, wx.ALIGN_TOP)

        self.gridSizer.Add(self.thresholdingSizer, 1, wx.EXPAND)

        #
        # Fourth step: Separation
        #

        self.separationSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.separatedImage = wx.StaticBitmap(
            self.panel, bitmap=wx.BitmapFromImage(emptyImage))
        self.separationSizer.Add(self.separatedImage)

        self.separationMethodSizer = wx.BoxSizer(wx.VERTICAL)
        self.separationMethodChooser = wx.RadioBox(self.panel,
                                                   choices=separation_methods,
                                                   style=wx.VERTICAL)
        self.separationMethodChooser.Bind(wx.EVT_RADIOBOX,
                                          self.onSeparationMethodChanged)
        self.separationMethodSizer.Add(self.separationMethodChooser)
        self.separationSizer.Add(self.separationMethodSizer)

        self.gridSizer.Add(self.separationSizer, 1, wx.EXPAND)

        #
        # Control buttons to proceed to next step
        #

        self.controlSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.nextButton = wx.Button(self.panel, -1, 'Proceed to ROI editor',
                                    size=wx.Size(200, 40))
        self.nextButton.Bind(wx.EVT_BUTTON, self.onNextClicked)
        self.controlSizer.AddMany([
            (wx.StaticText(self, -1, ''), 5, wx.EXPAND),
            (self.nextButton, 1, wx.FIXED)
        ])

        #
        # finalize window
        #
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.gridSizer, 1, wx.EXPAND)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL | wx.EXPAND)
        self.mainSizer.Add(self.controlSizer, 0, wx.EXPAND)

        self.panel.SetSizer(self.mainSizer)
        self.panel.Fit()
        self.panel.SetAutoLayout(True)
        self.Layout()
        self.Fit()

        self.update()

    def update(self):
        if not hasattr(self, 'loader'):
            return

        if self.config['segmentation_source'] == 'first_frame':
            self.source = self.loader.get_frame(0)
        elif self.config['segmentation_source'] == 'mean':
            self.source = self.loader.get_mean()
        elif self.config['segmentation_source'] == 'variance':
            self.source = self.loader.get_variance()
        else:
            print("Error, no source method selected")
            return

        self.sourceImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(self.source)))

        self.filtered = analyzer.segmentation.\
            gaussian_filter(self.source, self.config['gauss_radius'])

        self.filteredImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(self.filtered)))

        # if no threshold is set yet, set one now
        if 'threshold' not in self.config:
            self.onLiButtonClicked(None)

        self.thresholded = analyzer.segmentation.\
            threshold(self.filtered, self.config['threshold'])

        self.thresholdedImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(self.thresholded)))

        if self.config['segmentation_algorithm'] == 'watershed':
            self.segmented = analyzer.segmentation.watershed(self.thresholded)
        elif self.config['segmentation_algorithm'] == 'randomwalk':
            self.segmented = analyzer.segmentation.\
                             random_walker(self.thresholded)
        elif self.config['segmentation_algorithm'] == 'kmeans':
            self.segmented = analyzer.segmentation.k_means(self.thresholded)
        elif self.config['segmentation_algorithm'] == 'fill':
            self.segmented = analyzer.segmentation.label(self.thresholded)

        self.separatedImage.SetBitmap(
            numpyToBitmap(greyscale16ToNormRGB(self.segmented)))

        self.panel.Fit()
        self.Layout()
        self.Fit()

    def setSegmenter(self, segmenter):
        self.segmenter = segmenter

    def setFile(self, path):
        self.path = path
        self.loader = analyzer.loader.open(path)

        self.update()

    def onNextClicked(self, event):
        self.nextFrame.setSource(self.source, self.segmented)
        self.nextFrame.Show()
        self.Close()

    def onSourceMethodChanged(self, event):
        self.config['segmentation_source'] = event.GetString()
        self.update()

    def onSeparationMethodChanged(self, event):
        self.config['segmentation_algorithm'] = event.GetString()
        self.update()

    def onThresholdChanged(self, event):
        self.config['threshold'] = float(event.GetPosition()) / 1000
        self.update()

    def onGaussRadiusChanged(self, event):
        self.config['gauss_radius'] = event.GetPosition()
        self.update()

    def onLiButtonClicked(self, event):
        self.config['threshold'] = analyzer.segmentation.\
                                   li_thresh_relative(self.filtered)
        self.update()
        self.thresholdSlider.SetValue(self.config['threshold'])

    def onOtsuButtonClicked(self, event):
        self.config['threshold'] = analyzer.segmentation.\
                                   otsu_thresh_relative(self.filtered)
        self.update()
        self.thresholdSlider.SetValue(self.config['threshold'])

    def onYenButtonClicked(self, event):
        self.config['threshold'] = analyzer.segmentation.\
                                   yen_thresh_relative(self.filtered)
        self.update()
        self.thresholdSlider.SetValue(self.config['threshold'])
