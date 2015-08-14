$('.btn-for-modal').on('click', function () {
	url = $(this).data("url");
	$("#modal_content").load(
		url,
  	    function () {
  	        $("#modal").modal();
  	    }
	);
});

$('.tag-button').on('click', function(){
	$("#div1").remove();
});

$(document).ready(function(){
	container = $(this).data("container");
    $('[data-toggle="tooltip"]').tooltip();   
});

//$('[data-toggle="tooltip"]').tooltip(); 