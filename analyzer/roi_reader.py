""" .roi or zipped roi files from ImageJ are loaded here"""
from lib import ijroi
import numpy


def open_roi(file_name, shape):
    if file_name.endswith(".zip"):
        roi_arr = ijroi.read_roi_zip(file_name, shape)
        roi = numpy.zeros(shape) > 0
        for r in roi_arr:
            roi = numpy.add(roi, r[1])
        return roi > 0
    else:
        with open(file_name, "rb") as f:
            roi = ijroi.read_roi(f, shape)
        return roi
