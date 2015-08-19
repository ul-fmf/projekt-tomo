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

MathJax.Hub.Config({
  tex2jax: {
    inlineMath: [["$", "$"], ["\\(", "\\)"]]
  }
});

$(document).ready(function() {
  $("code").each(function() {
      $(this).addClass("prettyprint")
  });
  prettyPrint();
  $('[data-toggle="tooltip"]').tooltip();
});
