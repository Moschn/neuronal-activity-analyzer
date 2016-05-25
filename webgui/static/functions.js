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

function show_popup(title, content) {
    $('#popup-title').html(title);
    $('#popup-content').html(content);
    $('#popup').modal('toggle');
}

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

function enable(obj) {
    $(obj).removeAttr('disabled');
}

function disable(obj) {
    $(obj).attr('disabled', 'disabled');
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
    return [max_index, max];
}
