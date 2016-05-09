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

    show_up_to('roi_editor');

    $.getJSON('/get_segmentation/' + videoname + '/' + run,
	      receive_segmentations);
}

function create_run_clicked() {
    run = $('#runname').val();
    $.post("/create_run/" + videoname + "/" + run, {},
	   display_runs, 'json');
}

function delete_run_clicked() {
    if(window.confirm('Are you sure you want to delete the run "'
		      + run + '"?')) {
	$.post("/delete_run/" + videoname + "/" + run, {},
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

    segmentation = data;
    
    var w = data['width'];
    var h = data['height'];

    draw_image_rgb_scaled($('#source_image')[0],
			  greyscale16_to_normrgb(data.source, w, h),
			  w, h);
    draw_image_rgb_scaled($('#filtered_image')[0],
			  greyscale16_to_normrgb(data.filtered, w, h),
			  w, h);
    draw_image_rgb_scaled($('#thresholded_image')[0],
			  greyscale16_to_normrgb(data.thresholded, w, h),
			  w, h);

    draw_image_rgb_scaled($('#segmented_image')[0],
			  greyscale16_to_normrgb(data.source, w, h),
			  w, h);
    draw_image_rgba_scaled($('#segmented_image')[0],
			   color_roi(data.segmented, w, h),
			   w, h);
    
    $.getJSON("/get_thresholds/" + videoname + '/' + run,
              function(data) { thresholds = data; });

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
    $('#summary2').html("");
    $('#rasterplot').html("");
    $('#plot').html("");
    $.post('/set_segmentation_params/' + videoname + '/' + run,
	   {
	       segmentation_source: source,
	       gauss_radius: gauss_radius,
	       threshold: threshold,
	       segmentation_algorithm: algorithm
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
    $('#saved_label').html("Unsaved changes!");
    editor_saved = false;
}

function changes_saved() {
    /* Show that the changes have been saved */
    $('#saved_label').html("Changes saved");
    editor_saved = true;
    show_up_to('roi_editor');
}

function editor_save() {
    /* Send the current segmentation in the editor to the server */
    var encoded_data = encode_array_8(segmentation.editor);
    $('#summary2').html("");
    $('#rasterplot').html("");
    $('#plot').html("");
    $.post('/set_edited_segmentation/' + videoname + '/' + run,
	   { edited_segmentation: encoded_data },
	   changes_saved);
}

function redraw_editor() {
    var layer0 = $('#editor_layer0')[0];
    var layer1 = $('#editor_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    draw_image_rgb_scaled(layer0,
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h);
    draw_image_rgba_scaled(layer0,
			   color_roi(segmentation.editor, w, h),
			   w, h);

    var layer1_ctx = layer1.getContext("2d");
    layer1_ctx.clearRect(0, 0, layer1.width, layer1.height);
    if(editor_active_neuron > 0) {
	var overlay = roi_overlay(segmentation.editor, w, h,
				  editor_active_neuron,
				  255, 255, 255, 80);
	draw_image_rgba_scaled(layer1, overlay, w, h);
    }
    if(editor_hovered_neuron > 0) {
	var hov_overlay = roi_overlay(segmentation.editor, w, h,
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
	    redraw_editor();
	}
    } else if(key == 'u') {
	if(editor_undo_stack.length > 0) {
	    segmentation.editor = editor_undo_stack.pop();
	    editor_not_saved();
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

function calculate_statistics_clicked() {
    if(!editor_saved) {
	if(!confirm("You have unsaved changes in the ROI editor? Calculate statistics anyway?")) {
	    return;
	}
    }
    
    current_stage = 'statistics';
    $.getJSON('/get_statistics/' + videoname + '/' + run, receive_statistics);
    
    var button = $('#statistics-button');
    button.html("Calculating...");
    button[0].disabled = 'disabled';
}

function receive_statistics(data) {
    // Save the data
    activities = data['activities'];
    spikes = data['spikes'];

    // Reset button and show statistics area
    var button = $('#statistics-button');
    button.html("Calculate statistics");
    button[0].disabled = '';
    show_up_to('statistics');

    // create plots
    //fig_roi = segmentation['roi']
    //mpld3.draw_figure("summary2", fig_roi)
    
    fig_raster = data['rasterplot']
    mpld3.draw_figure("rasterplot", fig_raster)

    fig_roi = data['roi']
    mpld3.draw_figure("summary2", fig_roi)

    // Show statistics in info line
    activity_calculation_time = data['time']['activity_calculation'];
    spike_detection_time = data['time']['spike_detection'];
    update_info_line();
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

$(document).ready(function() {
    $('#summary2').click(function(e) {
	var offset = $(this).offset();
	// Get coordinates on whole image
	var img_x = e.pageX - offset.left;
	var img_y = e.pageY - offset.top;
	//var img_w = $('#summary2').width();
	//var img_h = $('#summary2').height();
	var img_w = 400
	var img_h = 400
	// Get actual image in plot metrics
	// bbox is [x, y, w, h] of plot in coords from 0 to 1, where 0 is left
	// or bottom and 1 is right or top
	var bbox = fig_roi.axes[0].bbox;
	var plot_x = img_x - bbox[0] * img_w -15; 
	var plot_y = img_y - (1-bbox[1]-bbox[3]) * img_h;
	var plot_w = bbox[2] * img_w;
	var plot_h = bbox[3] * img_h;
	// Get coordinates on segmentation as integer
        var seg_x = Math.floor(plot_x * segmentation['width'] / plot_w);
	var seg_y = Math.floor(plot_y * segmentation['height'] / plot_h);
        neuron = (segmentation['segmented'][seg_y*segmentation['width'] + seg_x]);
	//if (plotted_neurons.indexOf(neuron) == -1) {
	//    plotted_neurons.push(neuron);
	//}
	$('#testcoords').html(seg_y + "|" + seg_x)
	update_plot(neuron);
    });
});

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
	$('#statistics-button-container')[0].style.display = 'none';
	$('#statistics')[0].style.display = '';
    }
}

function encode_array_8(arr) {
    /* Converts an array of 8 bit values to a base64 encoded string */
    var str = "";
    for(var i = 0; i < arr.length; ++i)
    {
	str += String.fromCharCode(arr[i]);
    }
    return btoa(str);
}

function encode_array_16(arr) {
    /* Converts an array of 16 bit values to a base64 encoded string */
    var str = "";
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
    var u8 = new Uint8Array(atob(data).split("").map(
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

function draw_image_rgb_scaled(canvas, img, w, h, alpha) {
    /* Takes a w*h*3 long array of 24 bit RGB pixel data and draws
       it on the canvas with an alpha value. The image is scaled to the size of
       the canvas.

       Args:
         canvas: A canvas object as returned by getDocumentById or $('#id')[0]
         img(w*h*3 Array): An array of length W*H*3 with values from 0-255
	 w, h: Size of the source image
	 alpha: transparency to use while drawing, defaults to 255 (opaque)
    */
    if (typeof(alpha) === 'undefined')
	alpha = 255;

    var temp_canvas = $("<canvas>")
	.attr("width", w).attr("height", h)[0];
    var temp_ctx = temp_canvas.getContext("2d");
    var imgData = temp_ctx.createImageData(w, h)
    
    for (var i = 0; i < w*h; ++i) {
	    imgData.data[4*i] = img[3*i];
	    imgData.data[4*i + 1] = img[3*i + 1];
	    imgData.data[4*i + 2] = img[3*i + 2];
	    imgData.data[4*i + 3] = alpha;
    }

    temp_ctx.putImageData(imgData, 0, 0);

    var ctx = canvas.getContext("2d");
    ctx.scale(canvas.width / w, canvas.height / h);
    ctx.drawImage(temp_canvas, 0, 0);
    ctx.setTransform(1, 0, 0, 1, 0, 0); // reset scaling
}

function draw_image_rgba_scaled(canvas, img, w, h) {
    /* Takes a w*h*4 long array of 32 bit RGBA pixel data and draws
       it on the canvas. The image is scaled to the size of the canvas.

       Args:
         canvas: A canvas object as returned by getDocumentById or $('#id')[0]
         img(w*h*4 Array): An array of length W*H*4 with values from 0-255
	 w, h: Size of the source image
    */
    var temp_canvas = $("<canvas>")
	.attr("width", w).attr("height", h)[0];
    var temp_ctx = temp_canvas.getContext("2d");
    var imgData = temp_ctx.createImageData(w, h)
    
    for (var i = 0; i < w*h*4; ++i) {
	imgData.data[i] = img[i];
    }

    temp_ctx.putImageData(imgData, 0, 0);

    var ctx = canvas.getContext("2d");
    ctx.scale(canvas.width / w, canvas.height / h);
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

function roi_overlay(roi, w, h, index, r, g, b, a) {
    /* Create an rgba image, where everything is transparent except for the roi
       indicated by index, which is in the color given by r,g,b and a */
    var img = new Uint8Array(w*h*4).fill(0);
    for(var i = 0; i < w*h; ++i) {
	if(roi[i] == index) {
	    img[4*i] = r;
	    img[4*i + 1] = g;
	    img[4*i + 2] = b;
	    img[4*i + 3] = a;
	}
    }
    return img;
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
