$(document).ready(
  function() {
    $('pre code').each(
      function() {
        $(this).addClass('python');
      }
    );
  }
);

$('.action, .status').tooltip({delay: { show: 500, hide: 100 }})
