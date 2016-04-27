import wx

from ui.image_conv import *
from analyzer.util import color_roi, greyscale16ToNormRGB, combine_images


class ROIEditor(wx.Frame):
    def __init__(self, parent, nextFrame, config):
        wx.Frame.__init__(self, parent,
                          title="Neural Activity Analyzer - ROI Editor")

        self.nextFrame = nextFrame

        # Visible region in the image view
        # [x1, y1, x2, y2]
        self.visible_region = [0., 1., 0., 1.]
        self.hovered_neuron = 0
        self.active_neuron = 0

        self.panel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        self.createWindows()

    def createWindows(self):
        # Create view
        emptyImage = wx.EmptyImage(800, 800)
        self.view = wx.StaticBitmap(self.panel,
                                    bitmap=wx.BitmapFromImage(emptyImage),
                                    size=wx.Size(1000, 1000))
        self.view.Bind(wx.EVT_MOTION, self.onViewMouseMove)
        self.view.Bind(wx.EVT_LEFT_UP, self.onViewClicked)
        self.panel.Bind(wx.EVT_CHAR, self.onViewKey)
        self.nextButton = wx.Button(self.panel, -1, 'Export data',
                                    size=wx.Size(200, 40))

        self.activityView1 = wx.StaticBitmap(
            self.panel,
            bitmap=wx.BitmapFromImage(emptyImage),
            size=wx.Size(800, 200))
        self.activityView2 = wx.StaticBitmap(
            self.panel,
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
        self.update()

    def update(self):
        if(not hasattr(self, 'segmentation') or
           not hasattr(self, 'segmentationSource')):
            return

        background = greyscale16ToNormRGB(self.segmentationSource)
        segmentation_overlay = color_roi(self.segmentation)

        image = combine_images([background, segmentation_overlay],
                               [0.8, 0.2])

        if self.hovered_neuron != 0:
            hovered_pixels = self.segmentation == self.hovered_neuron
            overlay = greyscale16ToNormRGB(hovered_pixels * 1.)
            image = combine_images([image, overlay],
                                   [1., 0.3])

        if self.active_neuron != 0:
            active_pixels = self.segmentation == self.active_neuron
            active_overlay = greyscale16ToNormRGB(active_pixels * 1.)
            image = combine_images([image, active_overlay],
                                   [1., 0.4])

        self.view.SetBitmap(numpy_to_bitmap_zoomed(image,
                                                   self.view.GetSize(),
                                                   self.visible_region))

    def onViewMouseMove(self, event):
        x = event.GetX()
        y = event.GetY()
        img_x, img_y = self._viewToImageCoords(x, y)

        hovered_neuron = self.segmentation[img_y, img_x]
        if self.hovered_neuron != hovered_neuron:
            self.hovered_neuron = hovered_neuron
            self.update()

    def onViewClicked(self, event):
        x = event.GetX()
        y = event.GetY()
        img_x, img_y = self._viewToImageCoords(x, y)

        clicked_neuron = self.segmentation[img_y, img_x]
        if clicked_neuron != self.active_neuron:
            self.active_neuron = clicked_neuron
            self.update()

    def onViewKey(self, event):
        if event.GetUniChar() == 109: # 'm'
            if self.active_neuron == 0 or self.hovered_neuron == 0:
                return
            neuron1 = min(self.active_neuron, self.hovered_neuron)
            neuron2 = max(self.active_neuron, self.hovered_neuron)

            self.segmentation[self.segmentation == neuron2] = neuron1
            self.update()

    def _viewToImageCoords(self, x, y):
        img_x = self.segmentationSource.shape[0] * x / self.view.GetSize().x
        img_y = self.segmentationSource.shape[0] * y / self.view.GetSize().y
        return img_x, img_y
