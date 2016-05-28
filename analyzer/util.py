import numpy
from types import ModuleType
from analyzer.defaults import default_config
import pkgutil

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


def color_roi(roi):
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


def load_config(path):
    config = {}

    try:
        d = ModuleType('config')
        with open(path) as f:
            exec(compile(f.read(), path, 'exec'), d.__dict__)
        for key in dir(d):
            config[key] = getattr(d, key)
    except IOError:
        print("config.py not found, using default")

    apply_defaults(config, default_config)
    return config


def save_config(config, path):
    """ Saves the config to a file """
    with open(path, 'w') as f:
        for k, v in config.items():
            if k.startswith('_'):
                continue
            if type(v) == int:
                f.write("%s = %i\n" % (k, v))
            elif type(v) == float:
                f.write("%s = %f\n" % (k, v))
            elif type(v) == numpy.float64:
                f.write("%s = %f\n" % (k, v))
            elif type(v) == str:
                f.write("%s = '%s'\n" % (k, v))
            else:
                print("Not saving config value %s of type %s" % (k, type(v)))


def get_default_config():
    config = {}
    apply_defaults(config, default_config)
    return config


def find_impl(package, name):
    """ Search in the package a module called <name> and find a class
    with the name <name> in that module, ignoring case in the name

    Example:
        find_impl(analyzer.spike_detection, "wdm")
        this will return analyzer.spike_detection.wdm.WDM
    """
    module = None

    searched_name = name.lower()
    searchpath = package.__path__._path

    for _, mod_name, _ in pkgutil.iter_modules(searchpath):
        if mod_name.lower() == searched_name:
            module = getattr(
                __import__(package.__name__, globals(), locals(), [mod_name]),
                mod_name)
            break

    if module is None:
        raise Exception("Implementation %s in %s not found! The file "
                        " should be named: %s.py"
                        % (name, package.__name__, name.lower()))

    for attr in dir(module):
        if attr.lower() == name.lower():
            return getattr(module, attr)

    raise Exception("module %s does notimport analyzer.thresholds.threshold contain any class named %s" %
                    (module.__name__, name))


def list_implementations(package, base_class):
    """ Given a package(or a module containing modules) list all subclasses of
    base_class implemented in those submodules """
    impls = []
    searchpath = package.__path__._path

    for _, mod_name, _ in pkgutil.iter_modules(searchpath):
        module = getattr(
                __import__(package.__name__, globals(), locals(), [mod_name]),
                mod_name)

        for attr_name, attr in module.__dict__.items():
            if not isinstance(attr, type):
                continue
            if(issubclass(attr, base_class) and
               attr != base_class and
               attr_name not in impls):
                impls.append((attr_name, attr))

    return impls
