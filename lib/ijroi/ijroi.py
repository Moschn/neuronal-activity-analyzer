# Copyright: Luis Pedro Coelho <luis@luispedro.org>, 2012
#            Tim D. Smith <git@tim-smith.us>, 2015
# License: MIT

import numpy as np
from math import floor, sqrt, atan2, cos, sin


def read_roi(fileobj, shape):
    '''
    points = read_roi(fileobj)

    Read ImageJ's ROI format. Points are returned in a nx2 array. Each row
    is in [row, column] -- that is, (y,x) -- order.
    '''
    # This is based on:
    # http://rsbweb.nih.gov/ij/developer/source/ij/io/RoiDecoder.java.html
    # http://rsbweb.nih.gov/ij/developer/source/ij/io/RoiEncoder.java.html

    SPLINE_FIT = 1
    DOUBLE_HEADED = 2
    OUTLINE = 4
    OVERLAY_LABELS = 8
    OVERLAY_NAMES = 16
    OVERLAY_BACKGROUNDS = 32
    OVERLAY_BOLD = 64
    SUB_PIXEL_RESOLUTION = 128
    DRAW_OFFSET = 256

    class RoiType:
        POLYGON = 0
        RECT = 1
        OVAL = 2
        LINE = 3
        FREELINE = 4
        POLYLINE = 5
        NOROI = 6
        FREEHAND = 7
        TRACED = 8
        ANGLE = 9
        POINT = 10

    def get8():
        s = fileobj.read(1)
        if not s:
            raise IOError('readroi: Unexpected EOF')
        return ord(s)

    def get16():
        b0 = get8()
        b1 = get8()
        return (b0 << 8) | b1

    def get32():
        s0 = get16()
        s1 = get16()
        return (s0 << 16) | s1

    def getfloat():
        v = np.int32(get32())
        return v.view(np.float32)

    def ellipse(xm, ym, widthd, heightd, angle, shape):
        x = np.arange(0, shape[0])
        y = np.arange(0, shape[1])[:, None]
        ellipse = (((x-xm)*cos(angle)+(y-ym)*sin(angle))/widthd*2)**2 + (((x-xm)*sin(angle)-(y-ym)*cos(angle))/heightd*2)**2

        return ellipse <= 1

    def line(arr, x0, y0, x1, y1):
        "Bresenham's line algorithm"
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                arr[x, y] = True
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                arr[x, y] = True
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy        
        arr[x, y] = True
        return arr

    def floodFill(x, y, arr):
        toFill = set()
        toFill.add((x, y))
        while len(toFill) > 0:
            (x, y) = toFill.pop()
            if arr[x, y]:
                continue
            arr[x, y] = True
            toFill.add((x-1, y))
            toFill.add((x+1, y))
            toFill.add((x, y-1))
            toFill.add((x, y+1))
        return arr

    magic = fileobj.read(4)
    if magic != b'Iout':
        raise ValueError('Magic number not found')
    version = get16()

    # It seems that the roi type field occupies 2 Bytes, but only one is used
    roi_type = get8()
    # Discard second Byte:
    get8()

    if roi_type not in [RoiType.FREEHAND, RoiType.POLYGON, RoiType.RECT,
                        RoiType.POINT, RoiType.OVAL]:
        raise NotImplementedError('roireader: ROI type %s not supported'
                                  % roi_type)

    top = get16()
    left = get16()
    bottom = get16()
    right = get16()
    n_coordinates = get16()
    x1 = getfloat()
    y1 = getfloat()
    x2 = getfloat()
    y2 = getfloat()
    stroke_width = get16()
    shape_roi_size = get32()
    stroke_color = get32()
    fill_color = get32()
    subtype = get16()
    if subtype != 0 and not (subtype == 3 and roi_type == RoiType.FREEHAND):
        raise NotImplementedError('roireader: ROI subtype %s not supported (!= 0)' % subtype)
    options = get16()
    arrow_style = get8()
    arrow_head_size = get8()
    rect_arc_size = get16()
    position = get32()
    header2offset = get32()

    if roi_type == RoiType.RECT:
        if options & SUB_PIXEL_RESOLUTION:
            result = np.zeros(shape) > 0
            for i in range(x1, x1+x2):
                for j in range(y1, y1+y2):
                    result[i, j] = True
            return result
        else:
            result = np.zeros(shape) > 0
            for i in range(top, bottom):
                for j in range(left, right):
                    result[i, j] = True
            return result
    elif roi_type == RoiType.OVAL:
        if options & SUB_PIXEL_RESOLUTION:
            xm = x1 + (x1 + x2)//2
            ym = y1 + (y1 + y2)//2
            return ellipse(xm, ym, x2, y2, 0, shape)
        else:
            xm = top + bottom//2
            ym = left + right//2
            return ellipse(xm, ym, bottom, right, 0, shape)

    elif roi_type == RoiType.FREEHAND and subtype == 3:
        ex1 = float(x1)
        ey1 = float(y1)
        ex2 = float(x2)
        ey2 = float(y2)
        v = np.int32((arrow_style << 24) | (arrow_head_size << 16) |
                     rect_arc_size)
        aspect_ratio = v.view(np.float32)

        xm = ex1 + abs(ex1 - ex2)//2
        ym = ey1 + abs(ey1 - ey2)//2
        widthd = sqrt(abs(ex1-ex2)**2 + abs(ey1-ey2)**2)
        heightd = aspect_ratio * widthd
        angle = atan2(top-bottom, left-right)
        return ellipse(xm, ym, widthd, heightd, angle, shape)

    if options & SUB_PIXEL_RESOLUTION:
        getc = getfloat
        points = np.empty((n_coordinates, 2), dtype=np.float32)
        fileobj.seek(4*n_coordinates, 1)
    else:
        getc = get16
        points = np.empty((n_coordinates, 2), dtype=np.int16)

    points[:, 1] = [getc() for i in range(n_coordinates)]
    points[:, 0] = [getc() for i in range(n_coordinates)]

    if options & SUB_PIXEL_RESOLUTION == 0:
        points[:, 1] += left
        points[:, 0] += top

    arr = np.zeros(shape) > 0
    for idx, p1 in enumerate(points):
        p2 = points[(idx+1) % len(points)]
        arr = line(arr, p1[0], p1[1], p2[0], p2[1])

    arr = floodFill(floor(np.mean(points[:, 0])), floor(np.mean(points[:, 1])),
                    arr)

    # check if there are more values in the roi than oustside
    if np.sum(arr) > shape[0]*shape[1]:
        arr = not arr

    # from matplotlib import pyplot
    # pyplot.imshow(arr)
    # pyplot.show()

    return arr


def read_roi_zip(fname, shape):
    import zipfile
    with zipfile.ZipFile(fname) as zf:
        return [(n, read_roi(zf.open(n), shape)) for n in zf.namelist()]
