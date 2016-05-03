from flask import Blueprint, render_template, request, g
import json

from .util import session_load

roi_editor = Blueprint('roi_editor', __name__,
                       template_folder='templates')

@roi_editor.route('/roi_editor/<videoname>/<session>')
def editor(videoname, session):
    g.session = session
    segmentation_data = json.dumps(
        session_load(videoname, 'segmentation').tolist())
    
    return render_template('roi_editor.html',
                           segmentation_data=segmentation_data,
                           session=session,
                           videoname=videoname)
