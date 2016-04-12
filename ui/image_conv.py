""" Functions to convert numpy images for display """

import wx
import numpy

#
# Convert between different image formats
#

def numpyToBitmap(img):
    """ Convert numpy RGB array to wxpython bitmap
    """
    image = wx.EmptyImage(img.shape[0], img.shape[1])
    image.SetData(img.tostring())
    wxBitmap = image.ConvertToBitmap()
    return wxBitmap    

def normalizeImage256(img):
    """ Convert image to normalized grayscale from 0 to 255 """
    img_f = numpy.array(img, dtype=numpy.float32)
    brightness_max = numpy.amax(img_f)
    brightness_min = numpy.amin(img_f)    
    brightness_range = brightness_max - brightness_min
    img_norm = (img_f - brightness_min) / brightness_range * 255
    return numpy.array(img_norm, dtype=numpy.uint8)

def greyscale16ToNormRGB(img):
    # Convert to 8 bit
    img_8 = normalizeImage256(img)
    # Convert to RGB
    rgb = numpy.asarray(numpy.dstack((img_8, img_8, img_8)),
                        dtype=numpy.uint8)
    return rgb
