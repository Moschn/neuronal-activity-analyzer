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
var correlations = undefined;  // correlation functions for each neuron pair
var correlation_maximas = undefined;  // maximums of those functions


var treeData = undefined;

/*
 * functions to update the trees
 */

function update_tree() {
    $.getJSON('/get_tree/', receive_tree);
}
$(document).ready(update_tree);

function receive_tree(data) {
    treeData = data.nodes;
    sort_tree(treeData);
    $('#tree').treeview({data: treeData});
    $('#tree').treeview('collapseAll', { silent: true });
    $('#tree').on('nodeSelected', node_selected);

    // Repeat for the batch path choosing tree
    $('#batchTree').treeview({data: treeData});
    $('#batchTree').treeview('collapseAll', { silent: true });
}

function sort_tree(treeData) {
    if (treeData.length != 0) {
	
	for (var i = 0; i < treeData.length; i++) {
	    if ('nodes' in treeData[i]) {
		sort_tree(treeData[i].nodes);
	    }
	}
	treeData.sort(function (node1, node2) {
	    return node1.text.localeCompare(node2.text);
	});
    }
}



$(document).ready(function () {
    show_up_to('file_select');
});
