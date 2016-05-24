/* globals */

// Stores currently edited thing
// Used to warn for changes to earlier stages, which destroy data of later ones
// values: segmentation, roi_editor, statistics
var current_stage = 'segmentation';
var videoname = "";
var run = "";

var exposure_time = undefined;
var segmentation = undefined;
var activities = undefined;
var spikes = undefined;


/*
 * functions to update the trees
 */

function update_tree() {
    $.getJSON('/get_tree/', receive_tree);
}
$(document).ready(update_tree);

function receive_tree(data) {
    treeData = data.nodes;
    $('#tree').treeview({data: treeData});
    $('#tree').treeview('collapseAll', { silent: true });
    $('#tree').on('nodeSelected', node_selected);

    // Repeat for the batch path choosing tree
    $('#batchTree').treeview({data: treeData});
    $('#batchTree').treeview('collapseAll', { silent: true });
}

$(document).ready(function () {
    show_up_to('file_select');
});
