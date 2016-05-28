from flask import Blueprint, request, jsonify
import numpy

from .util import decode_array_8
from .runs import Run
import analyzer.segmentation

roi_editor_blueprint = Blueprint('roi_editor', __name__)


@roi_editor_blueprint.route(
    '/set_edited_segmentation/<path:videoname>/<runname>', methods=['POST'])
def set_edited_segmentation(videoname, runname):
    try:
        with Run(videoname, runname) as run:
            segmented = run['segmentation']

            encoded_data = request.values.get('edited_segmentation')
            edited_seg = decode_array_8(encoded_data,
                                        segmented['editor'].shape[0],
                                        segmented['editor'].shape[1])
            unique_neurons = numpy.unique(edited_seg)[1:]  # 0 is background
            filled_seg = numpy.zeros(edited_seg.shape, dtype='uint8')
            n = 1
            for i in unique_neurons:
                filled_seg[edited_seg == i] = n
                n += 1
            segmented['editor'] = filled_seg

            segmented['borders'] = analyzer.segmentation\
                                           .get_borders(segmented['editor'])

            run['segmentation'] = segmented
            run['statistics'] = None  # Invalidate statistics
        return jsonify(success=True)
    except Exception as e:
        return jsonify(fail=str(e))
