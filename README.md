# Neuronal Activity Analyzer

Neuronal activitiy analyzer is a tool for the analysis of neuronal activity data. It consists of a python library for the video analysis and of a webgui ([Demo](http://neurons.ee.ethz.ch)). 

More information can be found in the [report](docs/automated_analysis_of_neuronal_cultures.pdf). 

## Library
The library can also be used without the webgui, an example is in [batch.py](batch.py) or [analyzer/batch.py](analyzer/batch.py) for more details.

## Webgui
The webgui is written in Python and Flask. The webgui allows visual feedback for the various settings for the library. There is also an editor for the regions of interest for more manual approaches.

## Installation
In order to install all dependencies run

    pip install -r requirements

## Deployment
Using the standard webserver of flask (werkzeug):

    python3 guidevserver.py

or

    ./guidevserver.py

For the gevent server:

    python3 server.py

or

    ./server.py

## Dependencies

### Library

* [numpy](https://github.com/numpy/numpy)
* [pillow](https://github.com/python-pillow/Pillow)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [scikit-image](https://github.com/scikit-image/scikit-image)
* [scipy](https://github.com/scipy/scipy)

### Webgui

* [flask](https://github.com/pallets/flask)
* [flask-compress](https://github.com/lmeunier/flask-compressor)
* [mpld3](https://github.com/mpld3/mpld3)
* [gevent (optional)](https://github.com/gevent/gevent)
