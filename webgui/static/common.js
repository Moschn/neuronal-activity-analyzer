/* globals */

// Stores currently edited thing
// Used to warn for changes to earlier stages, which destroy data of later ones
// values: segmentation, roi_editor, statistics
var current_stage = 'segmentation';
var videoname = "";
var run = "";
var segmentation = undefined;
var activities = undefined;
var spikes = undefined;

/* 
 * Run management
 */

function videoname_clicked() {
    var new_videoname = $('#fileselect').find(":selected").text();
    if (new_videoname == videoname) {
	return;
    }
    videoname = new_videoname;
    
    show_up_to('file_select');
    
    // Update the list of runs for that file
    $.getJSON("/get_runs/" + videoname, display_runs);
}

function display_runs(data) {
    var options_as_string;
    for(var i = 0; i < data['runs'].length; ++i) {
        options_as_string += '<option>' + data['runs'][i] + '</option>';
    }
    $('#runselect').html(options_as_string);
}

function run_clicked() {
    var new_run = $('#runselect').find(":selected").text();
    if (new_run == run) {
	return;
    }
    run = new_run;

    show_up_to('statistics');

    $.getJSON('/get_segmentation/' + videoname + '/' + run,
	      display_segmentations);
}

function create_run_clicked() {
    run = $('#runname').val();
    $.post("/create_run/" + videoname + "/" + run, {},
	   display_runs, 'json');
}

function delete_run_clicked() {
    if(window.confirm('Are you sure you want to delete the run "'
		      + run + '"?')) {
	$.ajax({
	    url: "/delete_run/" + videoname + "/" + run,
	    type:' DELETE',
	    dataType: 'json',
	    success: display_runs,
	    error: function (jqXHR, textStatus, errorThrown) { 
		console.log(textStatus);
	    }
	});
    }
}

/* 
 * Segmentation
 */

var thresholds = {};
      
function display_segmentations(data) {
    /* Callback for an ajax query to get_segmentations, which displays the
       retrived images */

    segmentation = data;
    
    var w = data['width'];
    var h = data['height'];

    set_image_rgb($('#source_image')[0],
		  greyscale16_to_normrgb(data['source'], w, h), w, h);
    set_image_rgb($('#filtered_image')[0],
		  greyscale16_to_normrgb(data['filtered'], w, h), w, h);
    set_image_rgb($('#thresholded_image')[0],
		  greyscale16_to_normrgb(data['thresholded'], w, h), w, h);
    set_image_rgb($('#segmented_image')[0],
		  greyscale16_to_normrgb(data['segmented'], w, h), w, h);
    
    $.getJSON("/get_thresholds/" + videoname + '/' + run,
              function(data) { thresholds = data; });
}

function apply_li() {
    $('#threshold').val(thresholds['li']);
}
      
function apply_otsu() {
    $('#threshold').val(thresholds['otsu']);
}
      
function apply_yen() {
    $('#threshold').val(thresholds['yen']);
}

function segmentation_parameters_changed() {
    var source = $("input[name='segmentation_source']:checked").val();
    var gauss_radius = $('#gauss_radius').val();
    var threshold = $('#threshold').val();
    var algorithm = $("input[name='segmentation_algorithm']:checked").val();

    if (current_stage != 'segmentation') {
	if(!window.confirm('Changing the segmentation parameters regenerates the'
			  + ' segmentation results. All changes done in the ROI'
			  + ' editor or later will be lost! Are you sure?')) {
	    return;
	}
	current_stage = 'segmentation';
    }

    $.post('/set_segmentation_params/' + videoname + '/' + run,
	   {
	       segmentation_source: source,
	       gauss_radius: gauss_radius,
	       threshold: threshold,
	       segmentation_algorithm: algorithm
	   },
	   display_segmentations, 'json');
}

/* 
 * ROI editor
 */



/*
 * Statistics
 */

function calculate_statistics_clicked() {
    current_stage = 'statistics';
    $.getJSON('/get_statistics/' + videoname + '/' + run, receive_statistics);
    
    var button = $('#statistics-button');
    button.html("Calculating...");
    button[0].style.backgroundColor = '#A0A0A0';
}

function receive_statistics(data) {
    activities = data['activities'];
    spikes = data['spikes'];

    $('#statistics-button')[0].style.display = 'none';
    $('#statistics')[0].style.display = '';

    set_image_rgb($('#overview')[0],
		  greyscale16_to_normrgb(segmentation['segmented'],
					 segmentation['width'],
					 segmentation['height']),
		  segmentation['width'],
		  segmentation['height']);
}

function update_plot(neuron_index) {
    chart = $('#plot').highcharts({
        title: {
            text: 'Activity of Neurons',
            x: -20 //center
        },
        xAxis: {
            title: {
                text: 'frame'
            }
        },
        yAxis: {
            title: {
                text: 'brightness'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{
            name: 'Neuron ' + neuron_index,
            data: activities[neuron_index-1]
        }]
    });
    
    for(var i = 0; i < spikes[neuron_index-1].length; ++i) {
        chart.highcharts().xAxis[0].addPlotLine({
            color: 'red',
            value: spikes[neuron_index-1][i],
            width: 2
	});
    }
}

$(document).ready(function() {
    $('#overview').click(function(e) {
	var offset = $(this).offset();
	var x = e.pageX - offset.left;
	var y = e.pageY - offset.top;
        var real_x = x * segmentation['width'] / $('#overview').width();
	var real_y = y * segmentation['height'] / $('#overview').height();
        neuron = (segmentation['segmented'][Math.floor(real_y)*segmentation['width'] + Math.floor(real_x)]);
	//if (plotted_neurons.indexOf(neuron) == -1) {
	//    plotted_neurons.push(neuron);
	//}
	update_plot(neuron);
    });
});

/* 
 * General functions
 */

function show_up_to(stage) {
    /* Show only the sections up to the provided one. Values are
       file_select, segmentation, roi_editor, statistics */
    if (stage == 'file_select') {
	$('#segmentation')[0].style.display = 'none';
	$('#roi_editor')[0].style.display = 'none';
	$('#statistics-button')[0].style.display = 'none';
    } else if (stage =='segmentation') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = 'none';
	$('#statistics-button')[0].style.display = 'none';
    } else if (stage =='roi_editor') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = '';
	$('#statistics-button')[0].style.display = 'none';
    } else if (stage =='statistics') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = '';
	$('#statistics-button')[0].style.display = '';
    }
}

function set_image_rgb(canvas, img, w, h) {
    /* Takes a w*h*3 long array of 24 bit RGB pixel data and displays
       it in the canvas

       Args:
         canvas: A canvas object as returned by getDocumentById or $('#id')[0]
         img(w*h*3 Array): An array of length W*H*3 with values from 0-255
    */
    var ctx = canvas.getContext("2d");
    var imgData = ctx.createImageData(w, h)
    
    for (var i = 0; i < w*h; ++i) {
	    imgData.data[4*i] = img[3*i];
	    imgData.data[4*i + 1] = img[3*i + 1];
	    imgData.data[4*i + 2] = img[3*i + 2];
	    imgData.data[4*i + 3] = 255;
    }

    ctx.putImageData(imgData, 0, 0);
}

function trans_draw_rgb_to_canvas(canvas, img, w, h, alpha) {
    /* Take a w*h*3 long array of 24 bit RGB pixel data and draw it in the
       canvas over the existing image. Use the provided alpha as transparency
    */
    var ctx = canvas.getContext("2d");
    
}

function greyscale16_to_normrgb(img, w, h) {
    /* Convert a width*height element array with 16 bit brightness data
       to a 24 bit rgb array with width*height*3 elements. The image is
       normalized to its dynamic range, so the darkest pixel is at 0 and
       the brightest at 255, with all other pixels scaled linear between
       those values.

       Args:
         img(w*h array): brightness data range 0-65535
         w(int): width
         h(int): height

       Returns:
         w*h*3 array, for each pixel red, green and blue in range 0-255
    */

    var brightest = arrayMax(img);
    var darkest = arrayMin(img);
    var range = brightest - darkest;
    
    var rgb = Array(w*h*3);
    for (var i = 0; i < w*h; ++i) {
	var brightness = (img[i] - darkest) / range * 255;
	rgb[3*i] = brightness;
	rgb[3*i + 1] = brightness;
	rgb[3*i + 2] = brightness;
    }
    return rgb
}

function arrayMin(arr) {
    /* From https://stackoverflow.com/questions/1669190/javascript-min-max-array-values */
    var len = arr.length, min = Infinity;
    while (len--) {
	if (arr[len] < min) {
	    min = arr[len];
	}
    }
    return min;
};

function arrayMax(arr) {
    /* From https://stackoverflow.com/questions/1669190/javascript-min-max-array-values */
    var len = arr.length, max = -Infinity;
    while (len--) {
	if (arr[len] > max) {
	    max = arr[len];
	}
    }
    return max;
};