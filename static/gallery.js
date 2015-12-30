/*!
 * EasyGal - A simple, photo gallery for the web based on Python3.
 *
 * License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 *
 * Copyright 2015 Andreas Hofmann
 *
 */

$( function() {
  var g_speed = 250;

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

    $('#main').animate({ opacity: 0.00 }, g_speed, function() {
      $('#main').load(baseurl+target, null, function() { 
        $('#main').animate({ opacity: 1.00 }, g_speed);

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

  var g_loggedIn;

  $(document).ready(function() {
    $('a.nav-button').each( function() {
      $(this).click( function() {
        navigate($(this).attr('id'));
      });
    });
    navigate($(".nav-button").first().attr('id'));
  });

  function showOverlay(id) {
    overlay = $(id);
    overlay.show('blind', g_speed);
    $('#overlay-trigger').switchClass('glyphicon-triangle-bottom', 'glyphicon-triangle-top', g_speed);

    $(document).click( function() { hideOverlays(); });
    overlay.click( function(e) { e.stopPropagation(); });
  }

  function hideOverlays() {
    $('.overlay').each(function() {
      overlay = $(this);
      overlay.find('input').each( function () {
        $(this).val('');
      });
      overlay.hide('blind', g_speed);
      $('#overlay-trigger').switchClass('glyphicon-triangle-top', 'glyphicon-triangle-bottom', g_speed);
      overlay = $('#login-overlay');

      $(document).click( function() {  });
      overlay.click( function(e) {  });
    });
  }

  $('div.login-dropdown').click( function (e) {
    if ($('span#overlay-trigger').text()) {
        overlay = '#user-overlay';
    } else {
        overlay = '#login-overlay';
    }

    if ($(overlay).is(':hidden')) {
      showOverlay(overlay);
    } else {
      hideOverlays();
    }

    e.stopPropagation();
  });

  $('form#login-form').submit( function (event) {
    var submit = true;
    overlay = $('#login-overlay');
    overlay.find('input').each( function () {
      if ($(this).val() === '') {
        $(this).closest('.form-group').addClass('has-error has-feedback');
        submit = false;
      } else {
        $(this).closest('.form-group').removeClass('has-error has-feedback');
      }
    });

    event.preventDefault();

    if (submit) {
      $('#login-btn').removeClass('btn-danger');
      $('#login-btn').addClass('btn-default');
      console.log('data='+$('form#login-form').serialize());
      $.ajax({
          url: '/login',
          type: 'POST',
          data: $('form#login-form').serialize(),
          success: function(data) {
            if (data) {
                hideOverlays();
                $('#overlay-trigger').html(data);
            }
          },
          error: function(error) {
            console.log(error);
            $('#login-btn').switchClass('btn-default', 'btn-danger', g_speed);
          }
      });
    }
  });

  $('#logout-btn').click( function () {
      $.ajax({
          url: '/logout',
          type: 'POST',
          data: $('form#login-form').serialize(),
          success: function(data) {
            if (data) {
                hideOverlays();
                $('#overlay-trigger').html('');
            }
          },
          error: function(error) {
            console.log(error);
            $.cookie("authorized", null, { path: '/' });
            $('#overlay-trigger').html('');
            hideOverlays();
          }
      });
  });

  function login(user) {
  }

  function logout() {
  }
});
