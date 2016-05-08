import numpy
from matplotlib import pyplot
from matplotlib import gridspec
from skimage import segmentation
from math import ceil


def save(figure, filename):
    figure.savefig(filename, bbox_inches='tight')
    pyplot.close(figure)


def show_plot(figure):
    figure.show()


def plot_roi_bg(roi, bg, fg, pixel_per_um):
    bg_norm = _normalize8_img(bg)
    fg_norm = _normalize8_img(fg)

    borders = segmentation.find_boundaries(roi)

    frame_rgb = numpy.zeros((roi.shape[0], roi.shape[1], 3), dtype='uint8')
    frame_rgb[..., 0] = bg_norm
    frame_rgb[..., 1] = fg_norm
    frame_rgb[..., 0][borders] = 255
    frame_rgb[..., 1][borders] = 255

    figure = pyplot.figure(figsize=(5, 5))
    x_axis_end = roi.shape[0] * 1/pixel_per_um
    y_axis_end = roi.shape[1] * 1/pixel_per_um
    pyplot.imshow(frame_rgb[::-1], extent=[0, x_axis_end, 0, y_axis_end])
    for i in range(1, numpy.amax(roi)+1):
        coordinates_neuron = numpy.where(roi == i)
        pyplot.text((coordinates_neuron[1][0]+10) * 1/pixel_per_um,
                    (coordinates_neuron[0][0]+10) * 1/pixel_per_um,
                    i, fontsize=20, color='white')
    pyplot.xlabel("[um]")
    pyplot.ylabel("[um]")
    pyplot.tight_layout()
    return figure


def plot_roi(roi, frame, pixel_per_um):
    bg = numpy.zeros(frame.shape)
    return plot_roi_bg(roi, bg, frame, pixel_per_um)


def plot_spikes(activity, spikes):
    pyplot.style.use('seaborn-deep')
    fig = pyplot.figure()
    pyplot.plot(activity)
    for time in spikes:
        pyplot.axvline(time, color='r')
    return fig


def plot_rasterplot(spikes, exposure_time, nr_bins):
    pyplot.style.use('seaborn-deep')
    fig = pyplot.figure(figsize=(7, 5))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = pyplot.subplot(gs[0])
    ax2 = pyplot.subplot(gs[1])
    max_time = 0
    for i, spike in enumerate(spikes):
        if len(spike) > 0:
            ax1.vlines(spike.astype(float)*exposure_time, i+0.5, i+1.5)
            if numpy.max(spike) > max_time:
                max_time = numpy.max(spike)
    ax1.set_ylim(0.5, len(spikes) + 0.5)
    ax1.set_ylabel('Neuron')
    ax1.set_xlabel('time [s]')
    ax1.set_xlim(0, ceil(max_time * exposure_time))
    total_spikes = []
    for spike in spikes:
        for value in spike:
            total_spikes.append(value*exposure_time)
    n, bins, patches = ax2.hist(total_spikes, nr_bins)
    # pyplot.plot(n)
    ax2.set_ylabel('spikes')
    ax2.set_xlabel('time [s]')
    ax2.set_xlim(0, ceil(max_time * exposure_time))
    pyplot.tight_layout()
    # fig.subplots_adjust(hspace=0)
    return fig


def _normalize8_img(img):
    max_dif = numpy.max(img) - numpy.min(img)
    img_norm = (img - numpy.min(img))/max_dif * 2**8
    return img_norm.astype('uint8')


def _normalize16_img(img):
    max_dif = numpy.max(img) - numpy.min(img)
    img_norm = (img - numpy.min(img))/max_dif * 2**16
    return img_norm.astype('uint16')
