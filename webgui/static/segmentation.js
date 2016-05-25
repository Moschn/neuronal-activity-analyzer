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

    x_corr = draw_image_rgb_scaled($('#source_image')[0],
				   greyscale16_to_normrgb(segmentation.source, w, h),
				   w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#source_image')[0], x_corr, h-100, w,
			    segmentation.pixel_per_um);
    x_corr = draw_image_rgb_scaled($('#filtered_image')[0],
				   greyscale16_to_normrgb(segmentation.filtered, w, h),
				   w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#filtered_image')[0], x_corr, h-100, w,
			    segmentation.pixel_per_um);
    x_corr = draw_image_rgb_scaled($('#thresholded_image')[0],
				   greyscale16_to_normrgb(segmentation.thresholded, w, h),
				   w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#thresholded_image')[0], x_corr, h-100, w,
			    segmentation.pixel_per_um);
    x_corr = draw_image_rgb_scaled($('#segmented_image')[0],
				   greyscale16_to_normrgb(segmentation.source, w, h),
				   w, h, c_w, c_h-70);
    draw_image_pixel_per_um($('#segmented_image')[0], x_corr, h-100, w,
			    segmentation.pixel_per_um);
    x_corr = draw_image_rgba_scaled($('#segmented_image')[0],
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
