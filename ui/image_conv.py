""" Functions to convert numpy images for display """

import wx
import scipy.ndimage.interpolation
import scipy.misc
#
# From numpy to wx.Bitmap
#


def numpyToBitmap(img):
    """ Convert numpy RGB array to wxpython bitmap
    """
    image = wx.EmptyImage(img.shape[0], img.shape[1])
    image.SetData(img.tostring())
    wxBitmap = image.ConvertToBitmap()
    return wxBitmap


def numpy_to_bitmap_zoomed(image, size, visibleRegion=[0., 1., 0., 1.]):
    """ Take a numpy array of rgb data and zoom it to the correct
    size to display in an StaticBitmap window. A region in the image to display
    may be specified with x and y from 0 to 1.

    Args:
        image (numpy.array): source image
        size (wx.Size): target size
        visibleRegion ([float, float, float, float]): Visible region of the
            source image. The 4 coordinates define the rect with x1, x2, y1, y2
            with coordinates from 0. to 1.

    Returns:
        wx.Bitmap object
    """
    oldw = image.shape[0]
    oldh = image.shape[1]
    x1 = round(oldw * visibleRegion[0])
    x2 = round(oldw * visibleRegion[1])
    y1 = round(oldh * visibleRegion[2])
    y2 = round(oldh * visibleRegion[3])

    data = image[y1:y2, x1:x2]

    wratio = float(size.x) / image.shape[0]
    hratio = float(size.y) / image.shape[1]

    # zoomed = scipy.ndimage.interpolation.zoom(data,
    #                                           [hratio, wratio, 1],
    #                                           order=1)

    zoomed = scipy.misc.imresize(data, wratio, 'nearest')
    return numpyToBitmap(zoomed)
