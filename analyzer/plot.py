import numpy
from matplotlib import pyplot
from matplotlib import cm
from skimage import segmentation


def save(figure, filename):
    figure.savefig(filename, bbox_inches='tight')
    pyplot.close(figure)

def show_plot(figure):
    figure.show()

def plot_roi_bg(roi, bg, fg):
    bg_norm = _normalize8_img(bg)
    fg_norm = _normalize8_img(fg)

    borders = segmentation.find_boundaries(roi)

    frame_rgb = numpy.zeros((512, 512, 3), dtype='uint8')
    frame_rgb[..., 0] = bg_norm
    frame_rgb[..., 1] = fg_norm
    frame_rgb[..., 0][borders] = 255
    frame_rgb[..., 1][borders] = 255

    figure = pyplot.figure()
    pyplot.imshow(frame_rgb)
    for i in range(1, numpy.amax(roi)+1):
        coordinates_neuron = numpy.where(roi == i)
        pyplot.text(coordinates_neuron[1][0]+10,
                    coordinates_neuron[0][0]+10, i, fontsize=20, color='white')
    return figure

def plot_roi(roi, frame):
    fig = pyplot.figure()
    pyplot.imshow(roi)
    for i in range(1, numpy.amax(roi)+1):
        coordinates_neuron = numpy.where(roi == i)
        pyplot.text(coordinates_neuron[1][0]+10,
                    coordinates_neuron[0][0]+10, i, fontsize=20, color='white')
    return fig

def plot_spikes(activity, spikes):
    pyplot.style.use('seaborn-deep')
    fig = pyplot.figure()
    pyplot.plot(activity)
    for time in spikes:
        pyplot.axvline(time, color='r')
    return fig

def plot_rasterplot(spikes, exposure_time, nr_bins):
    pyplot.style.use('seaborn-deep')
    fig, (ax1, ax2) = pyplot.subplots(2)
    for i, spike in enumerate(spikes):
        ax1.vlines(spike.astype(float)*exposure_time, i+0.5, i+1.5)
    ax1.set_ylim(0.5, len(spikes) + 0.5)
    ax1.set_ylabel('Neuron')
    ax1.set_xlabel('time [s]')
    total_spikes = []
    for spike in spikes:
        for value in spike:
            total_spikes.append(value*exposure_time)
    n, bins, patches = ax2.hist(total_spikes, nr_bins)
    #pyplot.plot(n)
    ax2.set_ylabel('spikes')
    ax2.set_xlabel('time [s]')
    #fig.subplots_adjust(hspace=0)
    return fig
    
def _normalize8_img(img):
    max_dif = numpy.max(img) - numpy.min(img)
    img_norm = (img - numpy.min(img))/max_dif * 2**8
    return img_norm.astype('uint8')

def _normalize16_img(img):
    max_dif = numpy.max(img) - numpy.min(img)
    img_norm = (img - numpy.min(img))/max_dif * 2**16
    return img_norm.astype('uint16')
