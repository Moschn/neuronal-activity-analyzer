/* 
 * Run management
 */

function node_selected(event, node) {
    var new_videoname = get_selected_file_from_tree($('#tree'), node);

    if (new_videoname == videoname) {
	return;
    }
    videoname = new_videoname;

    show_up_to('file_select');

    // Update the list of runs for that file
    $.getJSON('/get_runs/' + videoname, receive_runs);
}

function receive_runs(data) {
    if(data.runs !== undefined) {
	var options_as_string = '';
	for(var i = 0; i < data['runs'].length; ++i) {
            options_as_string += '<option>' + data['runs'][i] + '</option>';
	}
	$('#runselect').html(options_as_string);

	enable('#runselect-container *');
	disable('#convert-button');
	$('#runselect').click(run_clicked);

	enable('#create-run-button');
    } else if(data.error === 'need_conversion') {
	disable('#runselect-container *');
	enable('#convert-button');
    } else if(data.error === 'is_folder') {
	disable('#runselect-container *');
	enable('#convert-button');
    } else {
	show_popup("Error!", data.error);
    }

    // Reset button text
    $('#create-run-button').html('Create run');
    enable($('#create-run-button'));
}

function convert_clicked() {
    $.post('/convert/' + videoname, {}, function() {
	$('#convert-button').html('Convert');
	update_tree();
    }, 'json');
    disable('#convert-button');
    $('#convert-button').html('Converting...');
}


$(document).ready(function(){
    $(document).on('click', '#runselect', run_clicked);
});

function run_clicked() {
    var new_run = $('#runselect').find(':selected').text();
    //if (new_run == run) {
    //    return;
    //}
    run = new_run;

    if(run === "")
	return;
    
    show_up_to('roi_editor');

    $.getJSON('/get_segmentation/' + videoname + '/' + run,
	      receive_segmentations);
}

function create_run_clicked() {
    run_t = $('#runname').val();
    $.post('/create_run/' + videoname + '/' + run_t, {},
	   receive_runs, 'json');

    disable('#create-run-button');
    $('#create-run-button').html('Creating run...');    
}

function delete_run_clicked() {
    if(window.confirm('Are you sure you want to delete the run "'
		      + run + '"?')) {
	$.post('/delete_run/' + videoname + '/' + run, {},
	       receive_runs, 'json');
    }
    return false;
}


var timestarted = undefined;
$(function () {
    'use strict';
    $('#fileupload').fileupload({
	url: '/upload',
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $('<p/>').text(file.name).appendTo(document.body);
            });
	    if (data.result.files.error != undefined) {
		alert(data.result.files.error);
	    }
        },
	progressall: function (e, data) {
	    if (timestarted == undefined) {
		timestarted = new Date().getTime();
	    }
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .progress-bar').css(
                'width',
                progress + '%'
            );
	    $('#progress-content').html(progress + '%');
	    var speed = data.loaded / (new Date().getTime() - timestarted) / 8;
	    $('#speed').html(speed + "KB/s");
        }
    });//.prop('disabled', !$.support.fileInput)
       // .parent().addClass($.support.fileInput ? undefined : 'disabled');
});
