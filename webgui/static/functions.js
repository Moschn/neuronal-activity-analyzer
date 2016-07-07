/* 
 * This file contains general utility functions
 */


/*
 * find selected file in a tree
 */

function get_selected_file_from_tree(tree, node) {
    var path = ""
    if (typeof tree.treeview('getParent', node.nodeId).nodeId == "undefined")
    {
	path = node.text;
    }
    else
    {
	path = node.text;
	var node_id = tree.treeview('getParent', node.nodeId).nodeId;
	var node_text = tree.treeview('getParent', node.nodeId).text;
	while(typeof node_id != "undefined")
	{
	    node_text = tree.treeview('getNode', node_id).text;
	    path = node_text + "/" + path;
	    node_id = tree.treeview('getParent', node_id).nodeId;
	}
    }
    return path;
}

/*
 * Popups and display
 */

function show_popup(title, content, width) {
    if(width == undefined)
	width = 600;
    $('#popup-title').html(title);
    $('#popup-content').html(content);
    $('#popup').children(".modal-dialog")[0].style.width = width;
    $('#popup').modal('toggle');
}

function show_up_to(stage) {
    /* Show only the sections up to the provided one. Values are
       file_select, segmentation, roi_editor, statistics */
    if (stage == 'file_select') {
	$('#segmentation')[0].style.display = 'none';
	$('#roi_editor')[0].style.display = 'none';
	$('#statistics-button-container')[0].style.display = 'none';
	$('#statistics-progress-indicator')[0].style.display = 'none';
	$('#statistics')[0].style.display = 'none';
    } else if (stage =='segmentation') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = 'none';
	$('#statistics-button-container')[0].style.display = 'none';
	$('#statistics-progress-indicator')[0].style.display = 'none';
	$('#statistics')[0].style.display = 'none';
    } else if (stage =='roi_editor') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = '';
	$('#statistics-button-container')[0].style.display = '';
	$('#statistics-progress-indicator')[0].style.display = 'none';
	$('#statistics')[0].style.display = 'none';
    } else if (stage =='statistics') {
	$('#segmentation')[0].style.display = '';
	$('#roi_editor')[0].style.display = '';
	$('#statistics-button-container')[0].style.display = '';
	$('#statistics-progress-indicator')[0].style.display = 'none';
	$('#statistics')[0].style.display = '';
    }
}

function enable(obj) {
    $(obj).removeAttr('disabled');
}

function disable(obj) {
    $(obj).attr('disabled', 'disabled');
}

function show_progress_indicator() {
    $("#progress-popup")[0].style.display = '';
}

function hide_progress_indicator() {
    $("#progress-popup")[0].style.display = 'none';
}

/*
 * Fullscreen plots
 */

var fullscreen_plot_old_parent = undefined;

function fullscreen_plot(plotdiv) {
    /* Displays the plot in the supplied div in a bootstrap modal */
    fullscreen_plot_old_parent = plotdiv;
    var highcharts_container = plotdiv.children(".highcharts-container");
    var chart = plotdiv.highcharts();

    // Show big popup
    show_popup("Plot", "<div id=\"popup-plot\"></div>", '80%');
    $("#popup-plot").height($(window).height() - 250);

    // Move plot to the modal popup
    highcharts_container.appendTo($("#popup-plot"));
    chart.renderTo = $("#popup-plot")[0];
    // Reflow the chart, when the modal animation finished
    setTimeout(function (chart) { chart.reflow(); }, 200, chart);

    // Set a handler to move the chart back when closing the modal
    $("#popup").on("hide.bs.modal", function (e) {
	$("#popup-plot").children(".highcharts-container")
			.appendTo(fullscreen_plot_old_parent);
	var chart = fullscreen_plot_old_parent.highcharts();
	chart.renderTo = fullscreen_plot_old_parent[0];
	chart.reflow();
    });
}

function activate_dblclick_zoom(plotdiv) {
    plotdiv.children(".highcharts-container").on("dblclick", fullscreen_plot.bind(undefined, plotdiv));
}

/*
 * encoding during transfer
 */

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

/*
 * min, max functions
 */

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

function arrayMaxIndex(arr) {
    var len = arr.length;
    var max_index = -1;
    var max = -Infinity;
    while (len--) {
	if (arr[len] > max) {
	    max_index = len;
	    max = arr[len];
	}
    }
    return max_index;
}
