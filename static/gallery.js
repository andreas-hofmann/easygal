/*!
 * EasyGal - A simple, photo gallery for the web based on Python3.
 *
 * License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 *
 * Copyright 2015 Andreas Hofmann
 *
 */

$( function() {
  function navigate(target) {
    _parent = $('.nav-button[id='+target+"]").parent('li');

    $('li.dropdown').removeClass('active');
    $('a.nav-button').each( function() {
      $(this).parent('li').removeClass('active');
    });

    baseurl = "/";
    trigger_fancybox = false

    if (_parent.hasClass('dropdown-button')) {
      $('li.dropdown').addClass('active');
      baseurl += "gallery/";
      trigger_fancybox = true
    }

    _parent.addClass('active');

    $('#main').animate({ opacity: 0.00 }, 500, function() {
      $('#main').load(baseurl+target, null, function() { 
        $('#main').animate({ opacity: 1.00 }, 500);

        if (trigger_fancybox) {
          $(".fancybox").fancybox({
              openEffect  : 'elastic',
              closeEffect : 'elastic',
              closeBtn    : false,
              arrows      : false,
              closeClick  : true,
              topRatio    : 0,
              padding     : 25,
              margin      : 15,
              nextEffect  : 'fade',
              prevEffect  : 'fade',
              autoCenter  : true,
              titleFromAlt: true,
              direction   : {
                  next : "bottom",
                  prev : "top"
              },
              afterLoad   : function () {
                  $.extend(this, {
                      jaspectRatio : false,
                      jtype    : 'html',
                      jwidth   : '100%',
                      jheight  : '100%',
                      jcontent : '<div class="fancybox-image" style="background-image:url(' + this.href +
                                 '); background-size: cover; background-position:50% 50%;background-repeat:no-repeat;height:100%;width:100%;" /></div>'
                  });
              },
              afterShow: function() {
                  $(".fancybox-title").wrapInner('<div />').show();
                  
                  $(".fancybox-wrap").hover(function() {
                      $(".fancybox-title").show();
                  }, function() {
                      $(".fancybox-title").hide();
                  });
              },
              helpers : {
                  title   : { type : 'inside' },
                  buttons : {},
                  overlay : {
                      css : { 'background' : 'rgba(0, 0, 0, 0.95)' }
                  },
                  title   : {
                      type : 'over'
                  }
              }
          });
        }

      });
    });
  }

  $(document).ready(function() {
    $('a.nav-button').each( function() {
      $(this).click( function() {
        navigate($(this).attr('id'));
      });
    });
    navigate($(".nav-button").first().attr('id'));
  });
});
