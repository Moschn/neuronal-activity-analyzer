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

    // Draw source image
    var canvas_size = fit_canvas_to_image($('#source_image')[0], w, h, 50);
    draw_image_rgb_scaled($('#source_image')[0],
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, canvas_size[0], canvas_size[1]-50);
    draw_scale_bar($('#source_image')[0], w, segmentation.pixel_per_um);

    // Draw filtered image
    canvas_size = fit_canvas_to_image($('#filtered_image')[0], w, h, 50);
    draw_image_rgb_scaled($('#filtered_image')[0],
			  greyscale16_to_normrgb(segmentation.filtered, w, h),
			  w, h, canvas_size[0], canvas_size[1]-50);
    draw_scale_bar($('#filtered_image')[0], w, segmentation.pixel_per_um);

    // Draw thresholded image
    canvas_size = fit_canvas_to_image($('#thresholded_image')[0], w, h, 50);
    draw_image_rgb_scaled($('#thresholded_image')[0],
			  greyscale16_to_normrgb(segmentation.thresholded, w, h),
			  w, h, canvas_size[0], canvas_size[1]-50);
    draw_scale_bar($('#thresholded_image')[0], w, segmentation.pixel_per_um);

    // Draw segmented image by drawing source and the borders above
    canvas_size = fit_canvas_to_image($('#segmented_image')[0], w, h, 50);
    draw_image_rgb_scaled($('#segmented_image')[0],
			  greyscale16_to_normrgb(segmentation.source, w, h),
			  w, h, canvas_size[0], canvas_size[1]-50);
    draw_scale_bar($('#segmented_image')[0], w, segmentation.pixel_per_um);
    draw_image_rgba_scaled($('#segmented_image')[0],
			   borders_overlay(segmentation.borders, w, h),
			   w, h, canvas_size[0], canvas_size[1]-50);
    
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
    redraw_editor_overlay();
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
