/*
 * Batch control
 */

function start_batch_clicked() {
    var batch_path = get_selected_file_from_tree(
	$('#batchTree'),
	$('#batchTree').treeview('getSelected')[0]);
    
    $.post('/start_batch/' + videoname + '/' + run, {batch_folder: batch_path},
	   receive_batch_started, 'json');

    $('#batch-start-button').html('Starting batch...');
    $('#batch-start-button').attr('disabled', 'disabled');
}

function receive_batch_started(data) {
    // Reset the batch folder chooser popup
    $('#batchFolderChooser').modal('toggle');
    $('#batch-start-button').html('Run batch');
    $('#batch-start-button').removeAttr('disabled');

    if (data.success !== undefined) {
	// Show message, that the process has started
	show_popup("Batch started",
		   "The batch process is now running in the background. "
		   + "Scroll to the top to see its progress or cancel the "
		   + "operation. Results will be stored on the itetnas02 NAS."
		  );
    } else {
	show_popup("Starting batch failed", data.fail);
    }
}

function stop_batch_clicked() {
    $.post('/stop_batch', {}, receive_batch_stopping, 'json');
    
    $('#batch-stop-button').html('Stopping batch...');
    $('#batch-stop-button').attr('disabled', 'disabled');
}

function receive_batch_stopping(data) {
    $('#batch-stop-button').html('Stop batch');
    $('#batch-stop-button').removeAttr('disabled');
    
    if(data.success !== undefined) {
	show_popup("Batch is stopping!", "This might take some time. The batch "
		   + "process has been notified to stop, but it might not "
		   + "receive the message until the current file has finished "
		   + "processing.");
    } else {
	show_popup("Batch could not be stopped!", data.fail);
    }
}

function update_batch_progress() {
    $.getJSON('/get_batch_progress', receive_batch_progress);

    setTimeout(update_batch_progress, 3000);
}
$(document).ready(update_batch_progress);

function receive_batch_progress(data) {
    if (data.success !== undefined) {
	// Batch is running, show progress bar
	percentage = 100 * data.processed_files / data.num_files;
	$('#batch-progress-bar').css('width', percentage+'%')
	    .attr('aria-valuenow', percentage);
	$('#batch-progress-bar').html("" + data.processed_files
				      + '/' + data.num_files);

	if(data.errors.length != 0) {
	    err_content = "";
	    data.errors.forEach(function (msg) {
		err_content += "<p>" + msg + "</p>";
	    });
	    
	    $('#batch-errors').html(err_content);
	    $('#batch-errors').css('display', '');
	} else {
	    $('#batch-errors').css('display', 'none');
	}

	$('#batch-status').css('display', '');
    } else {
	$('#batch-status').css('display', 'none');
    }
}
