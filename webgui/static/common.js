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

// editor overlay
var editor_overlay = undefined;
var statistics_overlay = undefined;

// Info line
var segmentation_time = undefined;
var activity_calculation_time = undefined;
var spike_detection_time = undefined;

var label_colors = [
    [0xff, 0x00, 0x00],
    [0x00, 0xff, 0x00],
    [0x00, 0x00, 0xff],
    [0x00, 0xff, 0xff],
    [0xff, 0x00, 0xff],
    [0xff, 0xff, 0x00],
    [0xff, 0x40, 0x00],
    [0x00, 0x40, 0xff],
    [0x40, 0x00, 0xff],
    [0x40, 0xff, 0x00],
    [0xff, 0x00, 0x40],
    [0x00, 0xff, 0x40],
    [0xff, 0x40, 0x40],
    [0x40, 0xff, 0x40],
    [0x40, 0x40, 0xff],
    [0xff, 0x80, 0x00],
    [0x00, 0x80, 0xff],
    [0x80, 0xff, 0x00],
    [0x80, 0x00, 0xff],
    [0x00, 0xff, 0x80],
    [0xff, 0x00, 0x80],
    [0x80, 0x80, 0xff],
    [0x80, 0xff, 0x80],
    [0xff, 0x80, 0x80]
]

7/* 
 * Run management
 */

// function videoname_clicked() {
//     var new_videoname = $('#fileselect').find(":selected").text();
//     if (new_videoname == videoname) {
// 	return;
//     }
//     videoname = new_videoname;
    
//     show_up_to('file_select');
    
//     // Update the list of runs for that file
//     $.getJSON("/get_runs/" + videoname, display_runs);
// }

$(document).ready(function() {
    $('#tree').on('nodeSelected', function(event, data) {
	
	var new_videoname = ""
	if (typeof $('#tree').treeview('getParent', data.nodeId).nodeId == "undefined")
	{
	    new_videoname = data.text;
	}
	else
	{
	    new_videoname = data.text;
	    var node_id = $('#tree').treeview('getParent', data.nodeId).nodeId;
	    var node_text = $('#tree').treeview('getParent', data.nodeId).text;
	    while(typeof node_id != "undefined")
	    {
		node_text = $('#tree').treeview('getNode', node_id).text;
		new_videoname = node_text + "/" + new_videoname;
		node_id = $('#tree').treeview('getParent', node_id).nodeId;
	    }
	}
	if (new_videoname == videoname) {
	    return;
	}
	videoname = new_videoname;
	
	show_up_to('file_select');
	
	// Update the list of runs for that file
	$.getJSON('/get_runs/' + videoname, display_runs);
	
    });
});

function display_runs(data) {
    var options_as_string = '';
    for(var i = 0; i < data['runs'].length; ++i) {
        options_as_string += '<option>' + data['runs'][i] + '</option>';
    }
    $('#runselect').html(options_as_string);
    $('#runselect').click(run_clicked);
}

$(document).ready(function(){
    $(document).on('click', '#runselect', run_clicked);
});

function run_clicked() {
    var new_run = $('#runselect').find(':selected').text();
    if (new_run == run) {
	return;
    }
    run = new_run;

    show_up_to('roi_editor');

    $.getJSON('/get_segmentation/' + videoname + '/' + run,
	      receive_segmentations);
}

function create_run_clicked() {
    run_t = $('#runname').val();
    $.post('/create_run/' + videoname + '/' + run_t, {},
	   display_runs, 'json');
    
}

function delete_run_clicked() {
    if(window.confirm('Are you sure you want to delete the run "'
		      + run + '"?')) {
	$.post('/delete_run/' + videoname + '/' + run, {},
	       display_runs, 'json');
    }
    return false;
}

/* 
 * Segmentation
 */

var thresholds = {};
      
function receive_segmentations(data) {
    /* Callback for an ajax query to get_segmentations, which displays the
       retrived images */

    segmentation = data['segmentation'];
    config = data['config'];
    
    var w = segmentation['width'];
    var h = segmentation['height'];

    var c_w = $('#source_image')[0].width;
    var c_h = $('#source_image')[0].height;

    draw_image_rgb_scaled($('#source_image')[0],
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#source_image')[0], 0, h-100, w,
			    segmentation.pixel_per_um);
    draw_image_rgb_scaled($('#filtered_image')[0],
			  greyscale16_to_normrgb(segmentation.filtered, w, h),
			  w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#filtered_image')[0], 0, h-100, w,
			    segmentation.pixel_per_um);
    draw_image_rgb_scaled($('#thresholded_image')[0],
			  greyscale16_to_normrgb(segmentation.thresholded, w, h),
			  w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#thresholded_image')[0], 0, h-100, w,
			    segmentation.pixel_per_um);
    draw_image_rgb_scaled($('#segmented_image')[0],
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#segmented_image')[0], 0, h-100, w,
			    segmentation.pixel_per_um);
    draw_image_rgba_scaled($('#segmented_image')[0],
			   color_roi_borders(segmentation.segmented,
					     segmentation.borders, w, h),
			   w, h, c_w, c_h-70);

    // set the webgui to the current config of the run
    $("input[id='seg_source_" + config['segmentation_source'] +
      "'][name='segmentation_source']").prop('checked', true);
    $("#gauss_radius").val(config['gauss_radius']);
    $("#threshold").val(config['threshold']);
    $("input[id='seg_algo_" + config['segmentation_algorithm'] +
      "'][name='segmentation_algorithm']").prop('checked', true);
    $("input[id='spike_algo_" + config['spike_detection_algorithm'] +
      "'][name='spike_algorithm']").prop('checked', true);
    $("#nSD_n").val(config['nSD_n']);

    thresholds = data['thresholds']
    //$.getJSON('/get_thresholds/' + videoname + '/' + run,
    //          function(data) { thresholds = data; });

    draw_editor();
    redraw_editor();
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
    var spike_algo = $("input[name='spike_algorithm']:checked").val();
    var nSD_n = $("#nSD_n").val();

    if (current_stage != 'segmentation') {
	if(!window.confirm('Changing the segmentation parameters regenerates the'
			  + ' segmentation results. All changes done in the ROI'
			  + ' editor or later will be lost! Are you sure?')) {
	    return;
	}
	current_stage = 'segmentation';
	show_up_to('roi_editor');
    }
    // clear plots in statisctics
    $('#summary2').html('');
    $('#rasterplot').html('');
    $('#plot').html('');
    statistics_active_neurons = [];
    $.post('/set_segmentation_params/' + videoname + '/' + run,
	   {
	       segmentation_source: source,
	       gauss_radius: gauss_radius,
	       threshold: threshold,
	       segmentation_algorithm: algorithm,
	       spike_detection_algorithm: spike_algo,
	       nSD_n: nSD_n
	   },
	   receive_segmentations, 'json');
}

/* 
 * ROI editor
 */

var editor_active_neuron = -1;
var editor_hovered_neuron = -1;
var editor_undo_stack = Array();
var editor_saved = true;

function editor_not_saved() {
    $('#editor_save').html('Unsaved changes!');
    $('#editor_save')[0].className = 'btn btn-danger';
    editor_saved = false;
}

function changes_saved() {
    /* Show that the changes have been saved */
    $('#editor_save').html('Changes saved!');
    $('#editor_save')[0].className = 'btn btn-success';
    editor_saved = true;
    show_up_to('roi_editor');
}

function editor_save() {
    /* Send the current segmentation in the editor to the server */
    var encoded_data = encode_array_8(segmentation.editor);
    $('#summary2').html('');
    $('#rasterplot').html('');
    $('#plot').html('');
    statistics_active_neurons = [];
    $.post('/set_edited_segmentation/' + videoname + '/' + run,
	   { edited_segmentation: encoded_data },
	   changes_saved);
    $.getJSON('/get_borders/' + videoname + '/' + run,
              function(data) { segmentation.borders = data; });
    var w = segmentation['width'];
    var h = segmentation['height'];
    draw_image_rgba_scaled($('#segmented_image')[0],
			   color_roi_borders(segmentation.segmented,
					     segmentation.borders, w, h),
			   w, h, $('#segmented_image')[0].width,
			   $('#segmented_image')[0].height-70);

}

function draw_editor() {
    var layer0 = $('#editor_layer0')[0];
    var layer1 = $('#editor_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    draw_image_rgb_scaled(layer0,
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h);
    draw_image_rgba_scaled(layer0,
			   color_roi(segmentation.editor, w, h),w, h);
}

function redraw_editor() {
    var layer0 = $('#editor_layer0')[0];
    var layer1 = $('#editor_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    
    var layer1_ctx = layer1.getContext('2d');
    layer1_ctx.clearRect(0, 0, layer1.width, layer1.height);
    if(editor_active_neuron > 0) {
	var overlay = editor_roi_overlay(segmentation.editor, w, h,
				  editor_active_neuron,
				  255, 255, 255, 80);
	draw_image_rgba_scaled(layer1, overlay, w, h);
    }
    if(editor_hovered_neuron > 0) {
	var hov_overlay = editor_roi_overlay(segmentation.editor, w, h,
				  editor_hovered_neuron,
				  255, 255, 255, 50);
	draw_image_rgba_scaled(layer1, hov_overlay, w, h);
    }
}

function editor_clicked(e) {
    var offset = $(this).offset();
    // Get coordinates on whole image
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var seg_x = Math.floor(x * segmentation['width'] / $(this)[0].offsetWidth);
    var seg_y = Math.floor(y * segmentation['height'] / $(this)[0].offsetHeight);
    editor_active_neuron = (segmentation['editor'][seg_y*segmentation['width'] + seg_x]);

    redraw_editor();
}
$(document).ready(function() {
    $('#editor_view').click(editor_clicked);
});

function editor_hovered(e) {
    var offset = $(this).offset();
    // Get coordinates on whole image
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var seg_x = Math.floor(x * segmentation['width'] / $(this)[0].offsetWidth);
    var seg_y = Math.floor(y * segmentation['height'] / $(this)[0].offsetHeight);
    editor_hovered_neuron = (segmentation['editor'][seg_y*segmentation['width'] + seg_x]);
    redraw_editor();
}
$(document).ready(function() {
    $('#editor_view').mousemove(editor_hovered);
});

function editor_keypress(e) {
    var key = String.fromCharCode(e.which);
    if(key == 'm') {
	if(editor_active_neuron > 0 && editor_hovered_neuron > 0) {
	    editor_undo_stack.push(new Uint8Array(segmentation.editor));

	    var dest = Math.min(editor_active_neuron, editor_hovered_neuron);
	    var src = Math.max(editor_active_neuron, editor_hovered_neuron);

	    for(var i = 0; i < segmentation.width * segmentation.height; ++i) {
		if(segmentation.editor[i] == src) {
		    segmentation.editor[i] = dest;
		}
	    }
	    editor_not_saved();
	    draw_editor();
	    redraw_editor();
	}
    } else if(key == 'd') {
	if(editor_active_neuron > 0) {
	    editor_undo_stack.push(new Uint8Array(segmentation.editor));

	    for(var i = 0; i < segmentation.width * segmentation.height; ++i) {
		if(segmentation.editor[i] == editor_active_neuron) {
		    segmentation.editor[i] = 0;
		}
	    }
	    editor_not_saved();
	    sraw_editor();
	    redraw_editor();
	}
    } else if(key == 'u') {
	if(editor_undo_stack.length > 0) {
	    segmentation.editor = editor_undo_stack.pop();
	    editor_not_saved();
	    draw_editor();
	    redraw_editor();
	}
    }
}
$(document).ready(function() {
    $('#editor_view').keypress(editor_keypress);
});

/*
 * Statistics
 */

var statistics_active_neurons = [];
var statistics_hovered_neuron = -1;

function calculate_statistics_clicked() {
    if(!editor_saved) {
	if(!confirm('You have unsaved changes in the ROI editor? Calculate statistics anyway?')) {
	    return;
	}
    }
    
    current_stage = 'statistics';
    $.getJSON('/get_statistics/' + videoname + '/' + run, receive_statistics);
    
    var button = $('#statistics-button');
    button.html('Calculating...');
    button[0].disabled = 'disabled';
}

$(document).ready(function() {
    $('#bin_form').submit(function(event) {
	event.preventDefault();
	var time_per_bin = $('#time_per_bin').val();
	$.getJSON('/get_statistics_rasterplot/' + videoname + '/' + run + '/' + time_per_bin,
		  function( data ) {
		      fig_raster = data['rasterplot'];
		      $('#rasterplot').empty();
		      mpld3.draw_figure('rasterplot', fig_raster);
		  });
    });
});

function statistics_draw_overview() {
    var layer0 = $('#statistics_layer0')[0];
    var layer1 = $('#statistics_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    var c_w = layer0.width;
    var c_h = layer0.height - 70;
    draw_image_rgb_scaled(layer0,
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, c_w, c_h);
    draw_image_rgba_scaled(layer0,
			   color_roi_borders(segmentation.editor,
					     segmentation.borders, w, h),
			   w, h, c_w, c_h);
    draw_image_pixel_per_um(layer0, 0, c_h+15, w, segmentation['pixel_per_um']);
    draw_image_neurons_number(layer0, segmentation.editor, w, h, c_w, c_h);
}

function statistics_redraw_overview() {
    var layer0 = $('#statistics_layer0')[0];
    var layer1 = $('#statistics_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    var c_w = layer0.width;
    var c_h = layer0.height - 70;
    
    var layer1_ctx = layer1.getContext('2d');
    layer1_ctx.clearRect(0, 0, layer1.width, layer1.height);
    if(statistics_hovered_neuron > 0) {
	var overlay = statistics_roi_overlay(segmentation.editor, w, h,
				  statistics_hovered_neuron,
				  255, 255, 255, 80);
	draw_image_rgba_scaled(layer1, overlay, w, h, c_w, c_h);
    }
    statistics_active_neurons.forEach(function (neuron) {
	var hov_overlay = statistics_roi_overlay(segmentation.editor, w, h,
				  neuron,
				  255, 255, 255, 50);
	draw_image_rgba_scaled(layer1, hov_overlay, w, h, c_w, c_h);
    })
}

function statistics_overview_clicked(e) {
    var offset = $(this).offset();
    // Get coordinates on whole image
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var seg_x = Math.floor(x * segmentation['width'] / $(this)[0].offsetWidth);
    var seg_y = Math.floor(y * segmentation['height'] / ($(this)[0].offsetHeight-70));
    neuron = (segmentation['editor'][seg_y*segmentation['width'] + seg_x]);
    if (neuron == 0) return;

    var index = statistics_active_neurons.indexOf(neuron);
    if(index != -1) {
	// If neuron is active, remove it from active list
	statistics_active_neurons.splice(index, 1);
    } else {
	// If neuron is not active add it to active list
	statistics_active_neurons.push(neuron);
    }
    statistics_redraw_overview();
    plot_active_neurons();
    redraw_rasterplot();
}
$(document).ready(function() {
    $('#overview').click(statistics_overview_clicked);
});

function statistics_overview_hovered(e) {
    var offset = $(this).offset();
    // Get coordinates on whole image
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var seg_x = Math.floor(x * segmentation['width'] / $(this)[0].offsetWidth);
    var seg_y = Math.floor(y * segmentation['height'] / ($(this)[0].offsetHeight-70));
    statistics_hovered_neuron = (segmentation['editor'][seg_y*segmentation['width'] + seg_x]);
    statistics_redraw_overview();
    plot_hovered_neuron(statistics_hovered_neuron);
}
$(document).ready(function() {
    $('#overview').mousemove(statistics_overview_hovered);
});

function receive_statistics(data) {
    // Save the data
    activities = data['activities'];
    spikes = data['spikes'];

    // Reset button and show statistics area
    var button = $('#statistics-button');
    button.html('Calculate statistics');
    button[0].disabled = '';
    show_up_to('statistics');

    // create plots
    //fig_roi = segmentation['roi']
    //mpld3.draw_figure('summary2', fig_roi)
    $('#rasterplot').empty();
    fig_raster = data['rasterplot']
    mpld3.draw_figure('rasterplot', fig_raster)
    raster = d3.select('.mpld3-figure');
    raster_rect = Array(activities.length)
    
    statistics_draw_overview();
    statistics_redraw_overview();

    // Show statistics in info line
    activity_calculation_time = data['time']['activity_calculation'];
    spike_detection_time = data['time']['spike_detection'];
    update_info_line();
}

$(document).ready(function() {
    $('#save_button').on('click', function() {
	var btn = $(this).button('loading');
	$.post('/save_plots/' + videoname + "/" + run, function(){
	    btn.button('reset');
	});
    });
});

function plot_active_neurons() {
    data = [];
    statistics_active_neurons.forEach(function (neuron) {
	data.push({
	    name: 'Neuron ' + neuron,
	    data: activities[neuron-1]
	});
    })
    chart = $('#plot_active').highcharts({
        title: {
            text: 'Activities',
            x: -20 //center
        },
        xAxis: {
            title: {
                text: 'frame'
            }
        },
        yAxis: {
            title: {
                text: 'brightness [max 65535]'
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
	credits: {
	    enabled: false
	},
        series: data
    });
}

function plot_hovered_neuron(neuron_index) {
    chart = $('#plot_hovered').highcharts({
        title: {
            text: 'Activity of hovered neuron',
            x: -20 //center
        },
        xAxis: {
            title: {
                text: 'frame'
            }
        },
        yAxis: {
            title: {
                text: 'brightness [max 65535]'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
	credits: {
	    enabled: false
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
    if (typeof spikes[neuron_index-1] != 'undefined')
    {
	for(var i = 0; i < spikes[neuron_index-1].length; ++i) {
            chart.highcharts().xAxis[0].addPlotLine({
		color: 'red',
		value: spikes[neuron_index-1][i],
		width: 2
	    });
	}
    }
}

function redraw_rasterplot()
{
    for (var i = 0; i < raster_rect.length; i++)
    {
	var img_w = $('#rasterplot').width();
	var img_h = $('#rasterplot').height();
	// Get actual image in plot metrics
	// bbox is [x, y, w, h] of plot in coords from 0 to 1, where 0 is left
	// or bottom and 1 is right or top
	// magic offset 8
	var bbox = fig_raster.axes[0].bbox;
	var y_offset = (1-bbox[1]-bbox[3])*img_h + (bbox[3]*img_h-4)/activities.length*(activities.length-i-1);
	var plot_x = bbox[0] * img_w;
	var width = bbox[2] * img_w;
	var height = bbox[3] * img_h / activities.length;
	if (statistics_active_neurons.indexOf(i+1) != -1)
	{
	    if (typeof raster_rect[i] == 'undefined')
	    {
		raster_rect[i] = raster.append('rect')
				       .attr('x', plot_x)
				       .attr('y', y_offset)
				       .attr('height', height)
				       .attr('width', width)
				       .attr('fill', 'yellow')
				       .attr('opacity', 0.3);
	    }
	}
	else
	{
	    if (typeof raster_rect[i] != 'undefined')
	    {
		raster_rect[i].remove();
		delete raster_rect[i];
	    }
	}
    }
}

/*
 * Info line
 */

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

    text += 'Developed at Laboratory for Biosensors and Bioelectronics';
    text += ', ETH Zurich';

    $('#infoline').html(text);
}

/* 
 * General functions
 */

function show_up_to(stage) {
    /* Show only the sections up to the provided one. Values are
       file_select, segmentation, roi_editor, statistics */
    if (stage == 'file_select') {
	$('#segmentation')[0].style.display = 'none';
	$('#roi_editor')[0].style.display = 'none';
	$('#statistics-button-container')[0].style.display = 'none';
	$('#statistics')[0].style.display = 'none';
    } else if (stage =='segmentation') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = 'none';
	$('#statistics-button-container')[0].style.display = 'none';
	$('#statistics')[0].style.display = 'none';
    } else if (stage =='roi_editor') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = '';
	$('#statistics-button-container')[0].style.display = '';
	$('#statistics')[0].style.display = 'none';
    } else if (stage =='statistics') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = '';
	$('#statistics-button-container')[0].style.display = '';
	$('#statistics')[0].style.display = '';
    }
}

function encode_array_8(arr) {
    /* Converts an array of 8 bit values to a base64 encoded string */
    var str = '';
    for(var i = 0; i < arr.length; ++i)
    {
	str += String.fromCharCode(arr[i]);
    }
    return btoa(str);
}

function encode_array_16(arr) {
    /* Converts an array of 16 bit values to a base64 encoded string */
    var str = '';
    for(var i = 0; i < arr.length; ++i)
    {
	str += String.fromCharCode(arr[i] >> 8);
	str += String.fromCharCode(arr[i] & 0xff);
    }
    return btoa(str);
}

function decode_array_8(data) {
    /* Takes a base64 encoded string and outputs an array of numbers, each
       representing 8 bit of the base64 encoded data */
    var u8 = new Uint8Array(atob(data).split('').map(
	function(c) {
	    return c.charCodeAt(0);
	}));
    return u8;
}

function decode_array_16(data) {
    /* Takes a base64 encoded string and outputs an array of numbers, each
       representing 16 bit of the encoded data */
    var u8 = decode_array_8(data);
    return new Uint16Array(u8.buffer);
}

function draw_image_rgb_scaled(canvas, img, w, h, c_w, c_h, alpha) {
    /* Takes a w*h*3 long array of 24 bit RGB pixel data and draws
       it on the canvas with an alpha value. The image is scaled to the size of
       the canvas.

       Args:
         canvas: A canvas object as returned by getDocumentById or $('#id')[0]
         img(w*h*3 Array): An array of length W*H*3 with values from 0-255
	 w, h: Size of the source image
         c_w, c_h: Size of the drawing space inside of the canvas
	 alpha: transparency to use while drawing, defaults to 255 (opaque)
    */
    if (typeof(alpha) === 'undefined')
	alpha = 255;

    var temp_canvas = $('<canvas>')
	.attr('width', w).attr('height', h)[0];
    var temp_ctx = temp_canvas.getContext('2d');
    var imgData = temp_ctx.createImageData(w, h)
    
    for (var i = 0; i < w*h; ++i) {
	    imgData.data[4*i] = img[3*i];
	    imgData.data[4*i + 1] = img[3*i + 1];
	    imgData.data[4*i + 2] = img[3*i + 2];
	    imgData.data[4*i + 3] = alpha;
    }

    temp_ctx.putImageData(imgData, 0, 0);

    var ctx = canvas.getContext('2d');
    if (typeof c_w == 'undefined')
    {
	c_w = canvas.width;
	c_h = canvas.height;
    }
    ctx.scale(c_w / w, c_h / h);
    ctx.drawImage(temp_canvas, 0, 0);
    
    ctx.setTransform(1, 0, 0, 1, 0, 0); // reset scaling
}

function draw_image_pixel_per_um(canvas, x, y, img_width, pixel_per_um) {
    var ctx = canvas.getContext('2d');
    
    var msd = Math.pow(10, Math.floor(Math.log10(img_width/pixel_per_um)));
    if ((img_width/pixel_per_um)/msd < 2)
    {
	msd = msd/10;
    }
    pixel_length = img_width * msd/(img_width/pixel_per_um);
    ctx.clearRect(0, y-5, img_width, 100);
		  
    ctx.beginPath();
    ctx.moveTo(x,y);
    ctx.lineTo(x+pixel_length,y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(x,y+5);
    ctx.lineTo(x,y-5);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(x+pixel_length,y+5);
    ctx.lineTo(x+pixel_length,y-5);
    ctx.stroke();

    ctx.font = '16px Arial';
    ctx.fillText(msd + 'um', x, y + 20);
}

function draw_image_neurons_number(canvas, roi, width, height, c_w, c_h) {
    var ctx = canvas.getContext('2d');
    ctx.save();
    ctx.fillStyle = 'white';
    for (var i = 1; i <= arrayMax(roi); i++) {
	var idx = roi.indexOf(i);
	var x = (idx % width) * c_w/width + 10;
	var y = (Math.floor(idx / width)) * c_h/height + 10;
	
	ctx.fillText(i, x, y);
    }
    ctx.restore();
}

function draw_image_rgba_scaled(canvas, img, w, h, c_w, c_h) {
    /* Takes a w*h*4 long array of 32 bit RGBA pixel data and draws
       it on the canvas. The image is scaled to the size of the canvas.

       Args:
         canvas: A canvas object as returned by getDocumentById or $('#id')[0]
         img(w*h*4 Array): An array of length W*H*4 with values from 0-255
	 w, h: Size of the source image
    */
    var temp_canvas = $('<canvas>')
	.attr('width', w).attr('height', h)[0];
    var temp_ctx = temp_canvas.getContext('2d');
    var imgData = temp_ctx.createImageData(w, h)
    
    for (var i = 0; i < w*h*4; ++i) {
	imgData.data[i] = img[i];
    }

    temp_ctx.putImageData(imgData, 0, 0);

    var ctx = canvas.getContext('2d');
    if (typeof c_w == 'undefined')
    {
	c_w = canvas.width;
	c_h = canvas.height;
    }
    ctx.scale(c_w / w, c_h / h);
    ctx.drawImage(temp_canvas, 0, 0);
    ctx.setTransform(1, 0, 0, 1, 0, 0); // reset scaling
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

function color_roi(roi, w, h) {
    /* Take an roi map of width w, and height h and create an rgba image, which
       has each roi in a different color. The background is transparent.

       Args:
           roi(uint8 array w*h): Map of the rois
	   w: width of the map
	   h: height of the map

       Returns:
           A rgba image of width w and height h as an array of w*h*4 elements in
	   the range from 0 to 255
    */
    var img = new Uint8Array(w*h*4);
    for(var i = 0; i < w*h; ++i)
    {
	if(roi[i] == 0) {
	    img[4*i] = 0;
	    img[4*i + 1] = 0;
	    img[4*i + 2] = 0;
	    img[4*i + 3] = 0;
	} else {
	    var index = (roi[i] - 1) % label_colors.length;
	    img[4*i] = label_colors[index][0];
	    img[4*i + 1] = label_colors[index][1];
	    img[4*i + 2] = label_colors[index][2];
	    img[4*i + 3] = 30;
	}
    }
    return img;
}

function color_roi_borders(roi, borders, w, h) {
    var img = color_roi(roi, w, h);
    for(var i = 0; i < w*h; i++)
    {
	if(borders[i] == true)
	{
	    img[4*i] = 255;
	    img[4*i+1] = 255;
	    img[4*i+2] = 0;
	    img[4*i+3] = 255;
	}
    }
    return img;
}

function editor_roi_overlay(roi, w, h, index, r, g, b, a) {
    /* Create an rgba image, where everything is transparent except for the roi
       indicated by index, which is in the color given by r,g,b and a */
    if(typeof editor_overlay == 'undefined') {
	editor_overlay = new Uint8Array(w*h*4);
    }
    editor_overlay.fill(0);
    for(var i = 0; i < w*h; ++i) {
	if(roi[i] == index) {
	    editor_overlay[4*i] = r;
	    editor_overlay[4*i + 1] = g;
	    editor_overlay[4*i + 2] = b;
	    editor_overlay[4*i + 3] = a;
	}
    }
    return editor_overlay;
}

function statistics_roi_overlay(roi, w, h, index, r, g, b, a) {
    /* Create an rgba image, where everything is transparent except for the roi
       indicated by index, which is in the color given by r,g,b and a */
    if(typeof statistics_overlay == 'undefined') {
	statistics_overlay = new Uint8Array(w*h*4);
    }
    statistics_overlay.fill(0);
    for(var i = 0; i < w*h; ++i) {
	if(roi[i] == index) {
	    statistics_overlay[4*i] = r;
	    statistics_overlay[4*i + 1] = g;
	    statistics_overlay[4*i + 2] = b;
	    statistics_overlay[4*i + 3] = a;
	}
    }
    return statistics_overlay;
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
}

function arrayMax(arr) {
    /* From https://stackoverflow.com/questions/1669190/javascript-min-max-array-values */
    var len = arr.length, max = -Infinity;
    while (len--) {
	if (arr[len] > max) {
	    max = arr[len];
	}
    }
    return max;
}

$(document).ready(update_info_line);
$(document).ready(function () {
    show_up_to('file_select');
});
