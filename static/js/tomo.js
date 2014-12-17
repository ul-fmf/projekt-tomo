$(document).ready(function(){
    $("code").each(function() {
        $(this).addClass("prettyprint")
    });
    prettyPrint();

    $('h4 > .action, h4 > .status, h2 > .action, h2 > .status').tooltip({
        delay: { show: 500, hide: 100 },
        placement: "left"
    });
    $('.action, .status').tooltip({
        delay: { show: 500, hide: 100 }
    });
});
