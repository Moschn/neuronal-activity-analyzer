from flask import Blueprint, render_template, request, g, send_file, current_app
import json
import os.path

from .util import session_load
import analyzer
from analyzer.integrator_sum import Integrator_sum

statistics = Blueprint('statistics', __name__,
                       template_folder='templates') 

@statistics.route('/displayable_image/<videoname>/<session>')
def displayable_image(videoname, session):
    g.session = session
    displayable = session_load(videoname, 'displayable')
    print(displayable)
    return send_file(displayable, mimetype='image/png')


@statistics.route('/statistics/<videoname>/<session>')
def statistics_page(videoname, session):
    g.session = session

    loader = analyzer.loader.open(
        os.path.join(current_app.config['VIDEO_FOLDER'], videoname))
    segmentation = session_load(videoname, 'segmentation')
    integrator = analyzer.integrator_sum.Integrator_sum(segmentation)
    activities = integrator.process_parallel_frames(loader)

    spikes = analyzer.detect_spikes(activities, {'spike_detection_algorithm': 'wavelet'})
    spikes = [ l.tolist() for l in spikes ]

    summary = []
    num_peaks = []
    total_peaks = 0
    for i in range(0, len(spikes)):
        num_peaks.append(len(spikes[i]))
        total_peaks += len(spikes[i])
        summary.append("Neuron %i:\t%i spikes" % (i, len(spikes[i])))
    summary.append("Total:\t%i spikes" % total_peaks)

    
    return render_template('statistics.html',
        segmentation_data=json.dumps(segmentation.tolist()),
        session=session,
        videoname=videoname,
        activity=json.dumps(activities.T.tolist()),
        spikes=json.dumps(spikes),
        summary=summary)
