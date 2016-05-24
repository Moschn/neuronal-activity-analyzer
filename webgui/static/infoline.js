/*
 * Info line
 */

// These variables get set by receive_statistics
var segmentation_time = undefined;
var activity_calculation_time = undefined;
var spike_detection_time = undefined;
var correlation_time = undefined;

function update_info_line() {
    var text = '';

    if (segmentation_time != undefined) {
	text += 'Segmentation time: ' + segmentation_time + 's | '
    }
    if (activity_calculation_time != undefined) {
	text += 'Activity calculation time: ' + activity_calculation_time + 's | '
    }
    if (spike_detection_time != undefined) {
	text += 'Spike detection time: ' + spike_detection_time + 's | '
    }
    if (correlation_time != undefined) {
	text += 'Correlation time: ' + correlation_time + 's | '
    }

    text += 'Developed at Laboratory for Biosensors and Bioelectronics';
    text += ', ETH Zurich';

    $('#infoline').html(text);
}
$(document).ready(update_info_line);
