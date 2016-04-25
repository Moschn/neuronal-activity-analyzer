import numpy

#
# Create labeled image from roi matrix
#

label_colors = [
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


def get_label_color(index):
    if index == 0:
        return (0, 0, 0)
    return label_colors[(index - 1) % len(label_colors)]


def roi_image(roi):
    """ Convert a ROI matrix to an image, where each pixel is colored in a
    different color according to its segment"""
    image_data = numpy.zeros((roi.shape[0], roi.shape[1], 3),
                             dtype=numpy.uint8)

    roi_count = numpy.amax(roi)
    for i in range(1, roi_count):
        image_data[roi == i] = get_label_color(i)

    return image_data

#
# superimpose segmentation and source image
#


def combine_images(imgs, alphas):
    """ Combine multiple rgb images in one rgb image """
    image_f = numpy.zeros(imgs[0].shape, dtype='float')
    for i in range(0, len(imgs)):
        image_f += alphas[i] * imgs[i]
    numpy.clip(image_f, 0., 255., image_f)
    return numpy.array(image_f, dtype='uint8')

#
# Convert between different image formats in numpy
#


def normalize_256(img):
    """ Normalize numpy array to the range from 0 to 255 """
    img_f = numpy.array(img, dtype=numpy.float32)
    brightness_max = numpy.amax(img_f)
    brightness_min = numpy.amin(img_f)
    brightness_range = brightness_max - brightness_min
    img_norm = (img_f - brightness_min) / brightness_range * 255
    return numpy.array(img_norm, dtype=numpy.uint8)


def greyscale16ToNormRGB(img):
    """ Take a numpy 16 bit greyscale image, normalize it and convert to rgb
    """
    # Convert to 8 bit
    img_8 = normalize_256(img)
    # Convert to RGB
    rgb = numpy.asarray(numpy.dstack((img_8, img_8, img_8)),
                        dtype=numpy.uint8)
    return rgb

#
# utility to merge configs
#


def apply_defaults(config, defaults):
    for k, v in defaults.items():
        if k not in config:
            config[k] = v
