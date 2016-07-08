# Neuronal Activity Analyzer

Neuronal activitiy analyzer is a tool for the analysis of neuronal activity data. It consists of a python library for the video analysis and of a webgui ([Demo](http://neurons.ee.ethz.ch)). 

More information can be found in the [report](docs/automated_analysis_of_neuronal_cultures.pdf). 

## Library
The library can also be used without the webgui, an example is in [batch.py](batch.py) or [analyzer/batch.py](analyzer/batch.py) for more details.

## Webgui
The webgui is written in Python and Flask. The webgui allows visual feedback for the various settings for the library. There is also an editor for the regions of interest for more manual approaches.

## Installation
The best way to install the library is to use a python virtual environment. There are packages for most distributions. Python 3 is recommended and required for the WebGUI to work.

For example on Debian based systems(i.e. Ubuntu) virtual environments can be used after installation using:

    sudo apt-get update; sudo apt-get install python-3pip virtualenv

A virtual environment can be created and all dependencies installed using:

    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

An easy way to use the tool is by running the development server with:

    ./guidevserver.py

Note that you have to activate the environment again, if you left the shell after installation, by running:

    . venv/bin/activate

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
