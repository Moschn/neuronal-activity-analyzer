/* 
 * ROI editor
 */

var editor_active_neuron = -1;
var editor_hovered_neuron = -1;
var editor_undo_stack = Array();
var editor_saved = true;
var editor_overlay = undefined;


function editor_not_saved() {
    $('#editor_save').html('Save unsaved changes!');
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
}

function draw_editor() {
    var layer0 = $('#editor_layer0')[0];
    var layer1 = $('#editor_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];

    var canvas_size = fit_canvas_to_image(layer0, w, h, 0);
    fit_canvas_to_image(layer1, w, h, 0);
    draw_image_rgb_scaled(layer0,
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, canvas_size[0], canvas_size[1]);
    draw_image_rgba_scaled(layer0,
			   color_roi(segmentation.editor, w, h), w, h,
			   canvas_size[0], canvas_size[1]);
}

function redraw_editor_overlay() {
    var layer1 = $('#editor_layer1')[0];
    var w = segmentation['width'];
    var h = segmentation['height'];
    
    var layer1_ctx = layer1.getContext('2d');
    layer1_ctx.clearRect(0, 0, layer1.width, layer1.height);
    if(editor_active_neuron > 0) {
	editor_overlay = roi_highlight_overlay(editor_overlay,
					       segmentation.editor, w, h,
					       editor_active_neuron,
					       255, 255, 255, 80);
	draw_image_rgba_scaled(layer1, editor_overlay, w, h,
			       layer1.width, layer1.height);
    }
    if(editor_hovered_neuron > 0) {
	editor_overlay = roi_highlight_overlay(editor_overlay,
					       segmentation.editor, w, h,
					       editor_hovered_neuron,
					       255, 255, 255, 50);
	draw_image_rgba_scaled(layer1, editor_overlay, w, h,
			       layer1.width, layer1.height);
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

    redraw_editor_overlay();
}
$(document).ready(function() {
    $('#editor_view').click(editor_clicked);
});

function editor_hovered(e) {
    if(segmentation === undefined) {
	return;
    }

    var offset = $(this).offset();
    // Get coordinates on whole image
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var seg_x = Math.floor(x * segmentation['width'] / $(this)[0].offsetWidth);
    var seg_y = Math.floor(y * segmentation['height'] / $(this)[0].offsetHeight);
    editor_hovered_neuron = (segmentation['editor'][seg_y*segmentation['width'] + seg_x]);
    redraw_editor_overlay();
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
	    redraw_editor_overlay();
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
	    draw_editor();
	    redraw_editor_overlay();
	}
    } else if(key == 'u') {
	if(editor_undo_stack.length > 0) {
	    segmentation.editor = editor_undo_stack.pop();
	    editor_not_saved();
	    draw_editor();
	    redraw_editor_overlay();
	}
    }
}
$(document).ready(function() {
    $('#editor_view').keypress(editor_keypress);
});
