#!/usr/bin/env python3
import analyzer.util
from analyzer.batch import analyze_all_in_folder
from sys import argv

# shutter time in s
# time_frame = 0.03


config = analyzer.util.load_config('config.py')

path = argv[1]

analyze_all_in_folder(path, config)
