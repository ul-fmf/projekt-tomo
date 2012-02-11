$(document).ready(
  function() {
    $('pre code').each(
      function() {
        $(this).addClass('python');
      }
    );
  }
);
$(function () {
  $("a[rel=popover]")
    .popover({
      offset: 10,
      placement: 'below',
      html: true,
    })
    .click(function(e) {
      e.preventDefault()
    })
})
