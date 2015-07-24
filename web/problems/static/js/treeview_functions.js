// Since confModal is essentially a nested modal it's enforceFocus method
// must be no-op'd or the following error results 
// "Uncaught RangeError: Maximum call stack size exceeded"
// But then when the nested modal is hidden we reset modal.enforceFocus
// http://stackoverflow.com/questions/21059598/implementing-jquery-datepicker-in-bootstrap-modal

var enforceModalFocusFn = $.fn.modal.Constructor.prototype.enforceFocus;
$.fn.modal.Constructor.prototype.enforceFocus = function() {};

// Global problem ID: set on open modal dialog. Tricky.
var problemId = null;

function copyProblem(selectedItem) {
	// Post to the URL that copies problem with ID problemID
	// to the problemset with id selectedItem.
	// On success redirect user to the new problemset.
	
	// MAKE POST_URL not static
	post_url = " /problems/" + problemId + "/" + selectedItem.id + "/copy/"
}

function prepareTreeData(data) {
	// Iterate through array.
	// Add text property to each node.
	// Its value must be the same as text.
	// On top level nodes change problem_sets to nodes.
	for (var i = 0; i < data.length; i++) {
	    o = data[i];
	    o.selectable = false;
		o.text = o.title;
		o.nodes = o.problem_sets;
		o.levels = 0;
		for (var j=0; j < o.nodes.length; j++) {
			ps = o.nodes[j];
			ps.text = ps.title;
		}
	}
}


function showTree() {
	//get list of courses (and their problem sets) where this user is teacher in JSON format
	var url = "/api/courses/?format=json";
	var jqxhr = $.getJSON(url, function() {
	}).done(function( data ) {
		    prepareTreeData(data);
			problem_tree = $('#problem_list_tree');
			problem_tree.treeview({data: data, levels: 1});
	}).fail(function( error ) {
		    console.log( "error" );
	});
}

function openModal(id, title) {
	problemId = id;
	$modal = $("#modal_copy");
	$modal_title = $("#modal_copy_problem_title");
	$modal_title.text(title);
	showTree();	
	$modal.modal('show');
}
