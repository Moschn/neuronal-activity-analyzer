import analyzer
from threading import Lock, Thread
from flask import current_app
from os import path, walk, stat
from analyzer.batch import analyze_file
from copy import deepcopy

batch_thread = None
batch_lock = Lock()

# all following variables must be locked using batch_lock!
is_running = False
requested_stop = False  # this tells the batch process to abort

# these are updated by the batch thread to show the progress
num_files = 0
processed = 0
batch_errors = []

def do_batch(path, config):
    global is_running
    global requested_stop
    global num_files
    global processed

    files_to_analyze = []
    for root, dirs, files in walk(path):
        for name in files:
            if stat('{}/{}'.format(root, name)).st_size > 100000000:
                files_to_analyze.append((name, root))

    with batch_lock:
        num_files = len(files_to_analyze)

    for f in files_to_analyze:
        try:
            analyze_file(f[0], f[1], config)
        except Exception as e:
            with batch_lock:
                batch_errors.append("Error while processing %s/%s: %s" % (f[1], f[0], str(e)))
        with batch_lock:
            processed += 1
            if requested_stop:
                print("Aborting batch on user request")
                break

    with batch_lock:
        is_running = False


def start_batch(folder, config):
    global is_running
    global batch_thread
    
    with batch_lock:
        if is_running:
            raise Exception("Batch is already running")

        is_running = True
        batch_thread = Thread(target=do_batch, args=(folder, deepcopy(config)))
        batch_thread.start()

        
def stop_batch():
    global requested_stop
    
    with batch_lock:
        if not is_running:
            raise Exception("Batch is not running")

        requested_stop = True


def get_progress():
    with batch_lock:
        if not is_running:
            raise Exception("Batch is not running")
        return (processed, num_files, batch_errors)
