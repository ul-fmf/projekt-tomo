
$(document).ready( function () { /* activate sidebar */
  $('#sidebar').affix({ offset: { top: 235 } });
  var $body   = $(document.body); /* activate scrollspy menu */
  $body.scrollspy({ target: '#rightCol', offset: 0 });
  $('a[href*=#]:not([href=#])').click(function() { /* smooth scrolling sections */
      if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
        var target = $(this.hash);
        target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
        if (target.length) {
          $('html,body').animate({ scrollTop: target.offset().top - 50 }, 1000);
          return false;
        }
      }
  });
});
