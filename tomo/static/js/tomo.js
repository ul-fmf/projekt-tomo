$(document).ready(function(){

    $("code").each(function() {
        $(this).addClass("prettyprint")
    });

    prettyPrint();

});

$('h4 > .action, h4 > .status, h2 > .action, h2 > .status').tooltip({delay: { show: 500, hide: 100 }, placement: "left"})
$('.action, .status').tooltip({delay: { show: 500, hide: 100 }})

$('#toggle').click(function() {
    $('#contents').css('margin-left', function(index, value) {
        if(value == "0px") { return "20px" } else { return "0px" }
    });
    $('#sidebar').toggle();
    $('#contents').toggleClass('span9');
    $('#contents').toggleClass('span12');
    $('#toggle').toggleClass('icon-chevron-left');
    $('#toggle').toggleClass('icon-chevron-right');
});

