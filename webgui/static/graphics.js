/*
 * This file contains functions to convert between image formats, plot arrays
 * on canvases and all other functions to create images
 */

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
 * drawing arrays onto canvases
 */

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

/*
 * converting image data
 */

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

/*
 * generating a color overlay from segmentation results
 */

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

function roi_highlight_overlay(target, roi, w, h, index, r, g, b, a) {
    /* Create an rgba image, where everything is transparent except for the roi
       indicated by index, which is in the color given by r,g,b and a */
    if(typeof target == 'undefined' || target.length != w*h*4) {
	target = new Uint8Array(w*h*4);
    }
    target.fill(0);
    for(var i = 0; i < w*h; ++i) {
	if(roi[i] == index) {
	    target[4*i] = r;
	    target[4*i + 1] = g;
	    target[4*i + 2] = b;
	    target[4*i + 3] = a;
	}
    }
    return target;
}
