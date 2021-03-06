/*
 * Statistics
 */

var statistics_active_neurons = [];
var statistics_hovered_neuron = undefined;
var statistics_last_hovered_neuron = 1;

var statistics_overlay = undefined;

var initiated_calculation = false;

function calculate_statistics_clicked() {
    if(!editor_saved) {
	if(!confirm('You have unsaved changes in the ROI editor? Calculate statistics anyway?')) {
	    return;
	}
    }
    
    current_stage = 'statistics';
    $.getJSON('get_statistics/' + videoname + '/' + run, receive_statistics);
    initiated_calculation = true;

    setTimeout(update_statistics_progress, 500);
    disable($("#statistics-button"));
}

function update_statistics_progress() {
    $.getJSON('get_statistics_progress/' + videoname + '/' + run, receive_statistics_progress);
}

function receive_statistics_progress(data) {
    if(data.running === true) {
	$('#statistics-button-container')[0].style.display = 'none';
	$('#statistics-progress-indicator')[0].style.display = '';

	var value = 100;
	var label = data.progress;
	if(data.progress == 'Loading' || data.progress == 'Processing frames')
	    value = 0;
	if(data.frames_done !== undefined) {
	    value = 100 * data.frames_done / data.frames_total;
	    label += '(' + data.frames_done + '/' + data.frames_total + ')';
	}

	$('#statistics-progress-bar').css('width', value + "%")
	    .attr('aria-valuenow', value);
	$('#statistics-progress-label').html(label);

	setTimeout(update_statistics_progress, 500);
    } else {
	enable($("#statistics-button"));
	if(data.finished && !initiated_calculation) {
	    // pull the results
	    $.getJSON('get_statistics/' + videoname + '/' + run, receive_statistics);
	}
    }
}

$(document).ready(function() {
    $('#bin_form').submit(function(event) {
	event.preventDefault();
	var time_per_bin = $('#time_per_bin').val();
	$.post('get_statistics_rasterplot/' + videoname + '/' + run,
	       {time_per_bin: time_per_bin},
	       function( data ) {
		   fig_raster = data['rasterplot'];
		   $('#rasterplot').empty();
		   mpld3.draw_figure('rasterplot', fig_raster);
	       },
	      'json');
    });
});

function statistics_draw_overview() {
    var layer0 = $('#statistics_layer0')[0];
    var layer1 = $('#statistics_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];

    var canvas_size = fit_canvas_to_image_grandparent(layer0, w, h, 50);
    fit_canvas_to_image_grandparent(layer1, w, h, 0);
    // Empty div width must be set using CSS, as it will not show when using
    // HTML attributes. Therefore we can't use fit_element_to_image
    $("#overview").width(canvas_size[0]);
    $("#overview").height(canvas_size[1]);
    draw_image_rgb_scaled(layer0,
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, canvas_size[0], canvas_size[1] - 50);
    draw_image_rgba_scaled(layer0,
			   borders_overlay(segmentation.borders, w, h),
			   w, h, canvas_size[0], canvas_size[1] - 50);
    draw_scale_bar(layer0, w, segmentation.pixel_per_um);
    draw_image_neurons_number(layer0, segmentation.editor, w, h,
			      canvas_size[0], canvas_size[1] - 50);
}

function statistics_redraw_overview_overlays() {
    var layer1 = $('#statistics_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    
    var layer1_ctx = layer1.getContext('2d');
    layer1_ctx.clearRect(0, 0, layer1.width, layer1.height);
    if(statistics_hovered_neuron > 0) {
	statistics_overlay = roi_highlight_overlay(statistics_overlay,
						   segmentation.editor, w, h,
						   statistics_hovered_neuron,
						   255, 255, 255, 120);
	draw_image_rgba_scaled(layer1, statistics_overlay, w, h,
			       layer1.width, layer1.height);
    }
    statistics_active_neurons.forEach(function (neuron) {
	statistics_overlay = roi_highlight_overlay(statistics_overlay,
						   segmentation.editor, w, h,
						   neuron,
						   255, 255, 255, 80);
	draw_image_rgba_scaled(layer1, statistics_overlay, w, h,
			       layer1.width, layer1.height);
    })
}

function overview_get_neuron_at(event) {
    var canvas = $('#statistics_layer1');
    var offset = canvas.offset();
    // Get coordinates on whole image
    var x = event.pageX - offset.left;
    var y = event.pageY - offset.top;
    var seg_x = Math.floor(x * segmentation['width'] / canvas[0].offsetWidth);
    var seg_y = Math.floor(y * segmentation['height'] / canvas[0].offsetHeight);
    return segmentation['editor'][seg_y*segmentation['width'] + seg_x];
}

function statistics_overview_clicked(e) {
    var neuron = overview_get_neuron_at(e);
    if (neuron == 0)
	return;

    var index = statistics_active_neurons.indexOf(neuron);
    if(index != -1) {
	// If neuron is active, remove it from active list
	statistics_active_neurons.splice(index, 1);
    } else {
	// If neuron is not active add it to active list
	statistics_active_neurons.push(neuron);
    }
    statistics_redraw_overview_overlays();
    plot_active_neurons();
    redraw_rasterplot();
}
$(document).ready(function() {
    $('#overview').click(statistics_overview_clicked);
});

function statistics_overview_hovered(e) {
    statistics_hovered_neuron = overview_get_neuron_at(e);

    if(statistics_hovered_neuron !== 0
       && statistics_hovered_neuron !== statistics_last_hovered_neuron) {
	statistics_last_hovered_neuron = statistics_hovered_neuron;
	redraw_single_activity_plot();
    }
    statistics_redraw_overview_overlays();
}
$(document).ready(function() {
    $('#overview').mousemove(statistics_overview_hovered);
});

function receive_statistics(data) {
    // reset initiated_calculation
    initiated_calculation = false;
    current_stage = 'statistics';

    if (data.success !== undefined) {
	// Save the data
	activities = data.activities;
	spikes = data.spikes;
	correlations = data.correlations;
	exposure_time = data.exposure_time;

	// show statistics area
	show_up_to('statistics');

	// Remove old data which might still be there
	$('#summary2').empty();
	$('#plot').empty();
	$('#rasterplot').empty();
	$('#correlation-heatmap').empty();
	statistics_active_neurons = [];
	statistics_hovered_neuron = undefined;
	statistics_last_clicked_neuron = 1;

	// create plots
	fig_raster = data['rasterplot']
	mpld3.draw_figure('rasterplot', fig_raster)
	raster = d3.select('.mpld3-figure');
	raster_rect = Array(activities.length)
    
	statistics_draw_overview();
	statistics_redraw_overview_overlays();
	plot_active_neurons();
	redraw_single_activity_plot();

	// correlation heatmap
	correlation_maximas = new Array();
	for(var i = 0; i < activities.length; ++i) {
	    var subarr = new Array();
	    for(var j = 0; j < activities.length; ++j) {
		var absCorrelations = new Array();
		for(var k = 0; k < correlations[i][j].length; ++k) {
		    absCorrelations.push(Math.abs(correlations[i][j][k]));
		}
		var maxIndex = arrayMaxIndex(absCorrelations);
		subarr.push([correlation_frame_index_to_time(maxIndex),
			    correlations[i][j][maxIndex]]);
	    }
	    correlation_maximas.push(subarr);
	}
	draw_correlation_heatmap();
	draw_correlation_function(1,2);

	// Show statistics in info line
	activity_calculation_time = data.time.activity_calculation;
	spike_detection_time = data.time.spike_detection;
	correlation_time = data.time.correlation;
	
	update_info_line();
    } else {
	show_popup('Calculating statistics failed!', data.fail);
    }

    enable('#statistics-button');
    $('#statistics-button').html('Calculate statistics');
}

$(document).ready(function() {
    $('#save_button').on('click', function() {
	var btn = $(this).button('loading');
	$.post('save_plots/' + videoname + "/" + run, function(){
	    btn.button('reset');
	});
    });
});

$(document).ready(function() {
    $('#download_button').on('click', function() {
	var btn = $(this).button('loading');
	$.post('save_plots/' + videoname + "/" + run, function(){
	    window.location.href = "/download/" + videoname + "-analysis";
	    btn.button('reset');
	});
    });
});

function plot_active_neurons() {
    data = new Array();
    statistics_active_neurons.forEach(function (neuron) {
	var points = new Array();
	for(var i = 0; i < activities[neuron-1].length; ++i) {
	    points.push([i * exposure_time, activities[neuron-1][i]]);
	}
	data.push({
	    name: 'Neuron ' + neuron,
	    data: points
	});
    })
    chart = $('#plot_active').highcharts({
        title: {
            text: 'Activities',
            x: -20 //center
        },
        xAxis: {
            title: {
                text: 'time [s]'
            }
        },
        yAxis: {
            title: {
                text: 'brightness [in std deviations]'
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
	plotOptions: {
	    series: {
		animation: false
	    }
	},
	chart: {
	    zoomType: 'x',
	},
        series: data
    });
    activate_dblclick_zoom($("#plot_active"));

    var c_index = 0;
    statistics_active_neurons.forEach(function (neuron) {
	for(var i = 0; i < spikes[neuron-1].length; ++i) {
            chart.highcharts().xAxis[0].addPlotLine({
		color: Highcharts.getOptions().colors[c_index],
		value: exposure_time * spikes[neuron-1][i],
		width: 2
	    });
	}
	c_index++;
    });
}

function redraw_single_activity_plot() {
    var neuron = statistics_last_hovered_neuron;

    var points = new Array();
    for(var i = 0; i < activities[neuron-1].length; ++i) {
	points.push([exposure_time * i, activities[neuron-1][i]]);
    }
    chart = $('#plot_hovered').highcharts({
        title: {
            text: 'Activity of hovered neuron',
            x: -20 //center
        },
        xAxis: {
            title: {
                text: 'time [s]'
            }
        },
        yAxis: {
            title: {
                text: 'brightness [in std deviations]'
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
	plotOptions: {
	    series: {
		animation: false
	    }
	},
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
	chart: {
	    zoomType: 'x',
	},
        series: [{
            name: 'Neuron ' + neuron,
            data: points
        }]
    });
    activate_dblclick_zoom($("#plot_hovered"));
    if (typeof spikes[neuron-1] != 'undefined')
    {
	for(var i = 0; i < spikes[neuron-1].length; ++i) {
            chart.highcharts().xAxis[0].addPlotLine({
		color: 'red',
		value: exposure_time * spikes[neuron-1][i],
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

function draw_correlation_heatmap() {
    data = new Array();
    for(var i = 0; i < correlation_maximas.length; ++i) {
	for(var j = 0; j < correlation_maximas.length; ++j) {
	    data.push([i+1, j+1, correlation_maximas[i][j][1]]);
	}
    }

    $('#correlation-heatmap').highcharts({
        chart: {
            type: 'heatmap',
            marginTop: 40,
            marginBottom: 80,
            plotBorderWidth: 1
        },

        title: {
            text: 'Maximum of correlation function of a neuron activity pair'
        },

        xAxis: {
            title: "First neuron",
	    tickInterval: 1
        },

        yAxis: {
            title: "Second neuron",
	    tickInterval: 1
        },

        colorAxis: {
	    max: 1,
            minColor: '#0000FF',
            maxColor: '#FF0000'
        },

        legend: {
            align: 'right',
            layout: 'vertical',
            margin: 0,
            verticalAlign: 'top',
            y: 25,
            symbolHeight: 280
        },

	credits: {
	    enabled: false
	},

        tooltip: {
            formatter: function () {
                return ('Maxium correlation of <b>neuron ' + this.point.x
			+ '</b> with a delayed <b>neuron ' + this.point.y
			+ '</b><br>: ' + this.point.value
			+ '<br>Delay of second neuron is [s]: '
			+ correlation_maximas[this.point.x-1][this.point.y-1][0]
		       );
            }
        },

	series: [{
            name: 'Maximum of correlation function',
            borderWidth: 1,
	    turboThreshold: 0,
            data: data,
	    events: {
		click: heatmap_clicked
	    }
        }],
    });
}

function draw_correlation_function(neuron1, neuron2) {

    var n_shifts = correlations[neuron1-1][neuron2-1].length;
    var data = new Array();
    for(var i = 0; i < n_shifts; ++i)
    {
	data.push([correlation_frame_index_to_time(i),
		   correlations[neuron1-1][neuron2-1][i]]);
    }

    chart = $('#correlation-function').highcharts({
        title: {
            text: ('Correlation of neuron ' + neuron1
		   + ' and neuron ' + neuron2),
            x: -20 //center
        },
        xAxis: {
            title: {
                text: 'Assumed delay to neuron ' + neuron2
            }
        },
        yAxis: {
            title: {
                text: 'correlation of activity'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
	legend: {
	    enable: false
	},
	credits: {
	    enabled: false
	},
	tooltip: {
            formatter: function () {
                return ('delay [s]: ' + this.point.x + '<br>corr: ' + this.point.y);
            }
        },
	chart: {
	    zoomType: 'x',
	},
        series: [{
	    name: ('Correlation function (neuron ' + neuron1 +
		   ' and ' + neuron2 + ')'),
            data: data
        }]
    });
    activate_dblclick_zoom($("#correlation-function"));
    chart.highcharts().xAxis[0].addPlotLine({
	color: 'red',
	value: correlation_maximas[neuron1-1][neuron2-1][0],
	width: 2
    });
}

function heatmap_clicked(event) {
    draw_correlation_function(event.point.x, event.point.y);
}

function correlation_frame_index_to_time(index) {
    return (index - correlations[0][0].length / 2) * exposure_time;
}
