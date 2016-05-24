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

	$('#runselect-container *').removeAttr('disabled');
	$('#convert-button')[0].disabled = 1;
	$('#runselect').click(run_clicked);
    } else if(data.error === 'need_conversion') {
	$('#runselect-container *').attr('disabled', 'disabled');
	$('#convert-button')[0].disabled = 0;
    } else {
	$('#runselect-container *').attr('disabled', 'disabled');
	$('#convert-button')[0].disabled = 1;
    }
}

function convert_clicked() {
    $.post('/convert/' + videoname, {}, function() {
	$('#convert-button').html('Convert');
	update_tree();
    }, 'json');
    $('#convert-button')[0].disabled = 1;
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

    show_up_to('roi_editor');

    $.getJSON('/get_segmentation/' + videoname + '/' + run,
	      receive_segmentations);
}

function create_run_clicked() {
    run_t = $('#runname').val();
    $.post('/create_run/' + videoname + '/' + run_t, {},
	   receive_runs, 'json');
    
}

function delete_run_clicked() {
    if(window.confirm('Are you sure you want to delete the run "'
		      + run + '"?')) {
	$.post('/delete_run/' + videoname + '/' + run, {},
	       receive_runs, 'json');
    }
    return false;
}
