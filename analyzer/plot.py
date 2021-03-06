import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib import gridspec
from skimage import segmentation
from math import ceil
import os
import analyzer.loader


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
    frame_rgb = frame_rgb[::-1]

    figure = pyplot.figure(figsize=(5, 5))
    x_axis_end = roi.shape[0] * 1/pixel_per_um
    y_axis_end = roi.shape[1] * 1/pixel_per_um
    pyplot.imshow(frame_rgb, extent=[0, y_axis_end, 0, x_axis_end])
    for i in range(1, numpy.amax(roi)+1):
        coordinates_neuron = numpy.where(roi == i)
        pyplot.text((coordinates_neuron[1][0]+10) * 1/pixel_per_um,
                    (coordinates_neuron[0][0]+10) * 1/pixel_per_um,
                    i, fontsize=20, color='white')
    pyplot.xlabel("[um]")
    pyplot.ylabel("[um]")
    pyplot.tight_layout()
    return figure


def save_roi(roi, frame, pixel_per_um, filename, analysis_folder):
    improved_roi = False
    directory = os.path.dirname(filename)
    if directory == '':
        directory = '.'
    files = [f for f in os.listdir(directory) if
             os.path.isfile(os.path.join(directory, f))]
    for f in files:
        fn = os.path.join(directory, f)
        try:
            if f.endswith((".tif",".tiff")) and os.stat(fn).st_size < 100000000:
                loader2 = analyzer.open_video(fn)
                fg_frame = loader2.get_frame(0)
                bg_frame = loader2.get_frame(1)

                figure = plot_roi_bg(roi, bg_frame, fg_frame, pixel_per_um)
                fname = os.path.join(analysis_folder, 'roi.svg')
                save(figure, fname)
                improved_roi = True
        except:
            print("No seperate imagefile with background/foreground found")
            print("Only basic plot of ROIs will be generated!")

    if not improved_roi:
        fname = os.path.join(analysis_folder, 'roi.svg')
        fig = plot_roi(roi, frame, pixel_per_um)
        save(fig, fname)


def plot_roi(roi, frame, pixel_per_um):
    bg = numpy.zeros(frame.shape)
    return plot_roi_bg(roi, bg, frame, pixel_per_um)


def plot_spikes(activity, spikes):
    pyplot.style.use('seaborn-deep')
    fig = pyplot.figure()
    pyplot.plot(activity)
    for time in spikes:
        pyplot.axvline(time, color='r')

    pyplot.xlabel('time [frames]')
    pyplot.ylabel('brightness [in std deviations]')
    return fig


def plot_rasterplot(spikes, exposure_time, time_per_bin):
    pyplot.style.use('seaborn-deep')
    fig = pyplot.figure(figsize=(9, 5))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = pyplot.subplot(gs[0])
    ax2 = pyplot.subplot(gs[1])
    max_time = 0
    for i, spike in enumerate(spikes):
        if len(spike) > 0:
            ax1.vlines(numpy.array(spike).astype(float)*exposure_time,
                       i+0.5, i+1.5)
            if numpy.max(spike) > max_time:
                max_time = numpy.max(spike)
    ax1.set_ylim(0.5, len(spikes) + 0.5)
    ax1.set_ylabel('Neuron')
    ax1.set_xlabel('time [s]')
    ax1.set_xlim(0, ceil(max_time * exposure_time))
    cut_time = max_time*exposure_time - ((max_time*exposure_time) %
                                         time_per_bin)
    total_spikes = []
    for spike in spikes:
        for value in spike:
            if value * exposure_time < cut_time:
                total_spikes.append(value*exposure_time)
    nr_bins = max_time*exposure_time//time_per_bin
    bins = numpy.linspace(0, cut_time, nr_bins+1)
    n, bins, patches = ax2.hist(total_spikes, bins)
    # pyplot.plot(n)
    ax2.set_ylabel('spikes')
    ax2.set_xlabel('time [s]')
    ax2.set_xlim(0, ceil(max_time * exposure_time))

    max_yticks = 4
    yloc = pyplot.MaxNLocator(max_yticks)
    ax2.yaxis.set_major_locator(yloc)

    pyplot.tight_layout()
    # fig.subplots_adjust(hspace=0)
    return fig


def plot_correlation_heatmap(correlation):
    correlation = numpy.array(correlation)
    fig = pyplot.figure()

    # calculate maximal correlation
    corr_maxima = numpy.zeros((correlation.shape[0], correlation.shape[1]))
    for neuron1 in range(0, correlation.shape[0]):
        for neuron2 in range(0, correlation.shape[1]):
            max_val = numpy.amax(correlation[neuron1, neuron2, :])
            min_val = numpy.amin(correlation[neuron1, neuron2, :])
            if numpy.abs(max_val) > numpy.abs(min_val):
                corr_maxima[neuron1][neuron2] = max_val
            else:
                corr_maxima[neuron1][neuron2] = min_val

    im = pyplot.pcolormesh(corr_maxima)
    fig.colorbar(im)
    pyplot.ylim([0, corr_maxima.shape[0]])
    pyplot.xlim([0, corr_maxima.shape[1]])
    pyplot.title("Correlation Heatmap")
    pyplot.xlabel("First Neuron")
    pyplot.ylabel("Second Neuron")
    return fig


def plot_correlation_details(correlation):
    pyplot.style.use('seaborn-deep')
    fig = pyplot.figure()
    pyplot.plot(correlation)
    pyplot.xlabel('Time delay')
    pyplot.ylabel('Correlation')
    return fig


def _normalize8_img(img):
    max_dif = numpy.max(img) - numpy.min(img)
    img_norm = (img - numpy.min(img))/max_dif * 2**8
    return img_norm.astype('uint8')


def _normalize16_img(img):
    max_dif = numpy.max(img) - numpy.min(img)
    img_norm = (img - numpy.min(img))/max_dif * 2**16
    return img_norm.astype('uint16')
