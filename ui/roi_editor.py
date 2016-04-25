import wx
import numpy

from ui.image_conv import *
from analyzer.util import roi_image, greyscale16ToNormRGB, combine_images

class ROIEditor(wx.Frame):
    def __init__(self, parent, nextFrame, config):
        wx.Frame.__init__(self, parent,
                          title="Neural Activity Analyzer - ROI Editor")

        self.nextFrame = nextFrame

        # Visible region in the image view
        # [x1, y1, x2, y2]
        self.visibleRegion = [0., 1., 0., 1.]
        self.hovered_neuron = 0
        
        self.panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        self.createWindows()

    def createWindows(self):
        
        # Create view
        emptyImage = wx.EmptyImage(800, 800)
        self.view = wx.StaticBitmap(self.panel,
                                    bitmap=wx.BitmapFromImage(emptyImage),
                                    size=wx.Size(1000, 1000))
        self.view.Bind(wx.EVT_MOTION, self.onViewMouseMove)

        self.activityView1 = wx.StaticBitmap(self.panel,
                                             bitmap=wx.BitmapFromImage(emptyImage),
                                             size=wx.Size(800, 200))
        self.activityView2 = wx.StaticBitmap(self.panel,
                                             bitmap=wx.BitmapFromImage(emptyImage),
                                             size=wx.Size(800, 200))
        # Create layout
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.view)
        self.activitySizer = wx.BoxSizer(wx.VERTICAL)
        self.activitySizer.Add(self.activityView1)
        self.activitySizer.Add(self.activityView2)
        self.mainSizer.Add(self.activitySizer)

        self.panel.SetSizer(self.mainSizer)
        self.panel.Fit()
        self.panel.SetAutoLayout(True)
        self.Layout()
        self.Fit()

    def setSource(self, source, segmentation):
        self.segmentationSource = source
        self.segmentation = segmentation
        self._drawBackground()
        self._drawSegmentation()
        self.update()

    def update(self):
        if(not hasattr(self, 'segmentation') 
           or not hasattr(self, 'segmentationSource')):
            return

        image = self.background_with_seg
        
        if self.hovered_neuron != 0:
            hovered_pixels = self.segmentation == self.hovered_neuron
            overlay = greyscale16ToNormRGB(hovered_pixels * 1.)
            image = combine_images([self.background_with_seg, overlay],
                                   [1., 0.3])
        
        self.view.SetBitmap(numpy_to_bitmap_zoomed(image,
                                                   self.view.GetSize(),
                                                   self.visibleRegion))
        
    def _drawBackground(self):
        self.background = greyscale16ToNormRGB(self.segmentationSource)

    def _drawSegmentation(self):
        segmentation_overlay = roi_image(self.segmentation)
        
        self.background_with_seg = combine_images([self.background,
                                                   segmentation_overlay],
                                                  [0.8, 0.2])

    def onViewMouseMove(self, event):
        x = event.GetX()
        y = event.GetY()
        img_x, img_y = self._viewToImageCoords(x, y)

        hovered_neuron = self.segmentation[img_y, img_x]
        if self.hovered_neuron != hovered_neuron:
            self.hovered_neuron = hovered_neuron
            print "Over neuron %i" % self.hovered_neuron
            self.update()

    def onViewClicked(self, event):
        x = event.GetX()
        y = event.GetY()
        img_x, img_y = self._viewToImageCoords(x, y)

        clicked_neuron = self.segmentation[img_y, img_x]
        if clicked_neuron != self.active_neuron:
            self.active_neuron = clicked_neuron
        
    def _viewToImageCoords(self, x, y):
        img_x = self.segmentationSource.shape[0] * x / self.view.GetSize().x
        img_y = self.segmentationSource.shape[0] * y / self.view.GetSize().y
        return img_x, img_y
