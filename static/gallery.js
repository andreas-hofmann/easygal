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
    _parent = $('.nav-button[id="'+target+'"]').parent('li');

    $('li.dropdown').removeClass('active');
    $('a.nav-button').each( function() {
      $(this).parent('li').removeClass('active');
    });

    baseurl = "/";
    trigger_fancybox = false

    enableDelete(false);

    if (_parent.hasClass('dropdown-button')) {
      $('li.dropdown').addClass('active');
      baseurl += "gallery/";
      trigger_fancybox = true;
    } else {
      $('#delete-btn').hide();
    }

    _parent.addClass('active');

    $('#main').animate({ opacity: 0.00 }, g_speed, function() {
      $('#main').load(baseurl+encodeURIComponent(target), null, function(response, status, xhr) {
        $('#main').animate({ opacity: 1.00 }, g_speed);

        if (status == "error") {
            $('#main').html("<div class='error'>Error: " + xhr.status + ": " + xhr.statusText);
            return;
        }

        if (trigger_fancybox) {
          $('#delete-btn').show();

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

  function showOverlay(id) {
    overlay = $(id);
    overlay.show('fade', g_speed);
    $('#overlay-trigger').switchClass('glyphicon-triangle-bottom', 'glyphicon-triangle-top', g_speed);

    $(document).click( hideOverlays );
    overlay.click( function(e) { e.stopPropagation(); });
  }

  function hideOverlays() {
    $('.overlay').each(function() {
      overlay = $(this);
      overlay.find('input').each( function () {
        $(this).val('');
      });
      overlay.hide('fade', g_speed);
      $('#overlay-trigger').switchClass('glyphicon-triangle-top', 'glyphicon-triangle-bottom', g_speed);
      overlay = $('#login-overlay');

      $(document).unbind('click', hideOverlays);
      overlay.unbind('click');

      $('#files').text('');
    });
  }

  $('div.login-dropdown').click( function (e) {
    if (!$('#upload-overlay').is(':hidden')) {
      hideOverlays();
      return;
    }

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

  $('#upload-btn').click( function() {
    $('#user-overlay').hide('fade', g_speed);

    var overlay = $('#upload-overlay');
    overlay.click( function(e) { e.stopPropagation(); });
    overlay.show('fade', g_speed);
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
      $('#login-btn').addClass('btn-primary');
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
            $('#login-btn').switchClass('btn-primary', 'btn-danger', g_speed);
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

  function handleGalleryChange() {
    if ($('input#upload-gallery').val().length > 0) {
      $('#fileupload-area').show('fade', g_speed);
      $('#fileupload').fileupload('option', { url: '/upload/' + $('input#upload-gallery').val() })
    } else {
      $('#fileupload-area').hide('fade', g_speed);
    }
  }

  $('#gallery-select').change( function() {
    var gallery = $('#upload-gallery');
    var index = $('#gallery-select').prop('selectedIndex');

    if (index === 0) {
      gallery.val('');
      $('#gallery-input-area').hide('fade', g_speed);
    } else if (index+1 === $('#gallery-select option').size()) {
      gallery.val('');
      $('#gallery-input-area').show('fade', g_speed);
    } else {
      gallery.val($('#gallery-select').val());
      $('#gallery-input-area').hide('fade', g_speed);
    }

    handleGalleryChange();
  });

  $('input#upload-gallery').on('change keyup paste', function() {
    handleGalleryChange();
  });

  $('#fileupload').fileupload({
      url: '/upload/',
      dataType: 'json',
      stop: function (e, data) {
        gallery = $('input#upload-gallery').val();

        if (!$('ul.dropdown-menu').has("li#"+gallery)) {
          $('ul.dropdown-menu').append('<li class="dropdown-button"><a class="nav-button" id="'
                                          +gallery+'" href="#">'+gallery+'</a></li>');
        }

        $(document).click( hideOverlays );
        navigate(gallery);
      },
      done: function (e, data) {
        $.each(data.result.files, function (index, file) {
            $('<p/>').text(file.name).appendTo('#files');
        });
        var progress = parseInt(data.loaded / data.total * 100, 10);
        $('#progress .progress-bar').css(
            'width', '0%'
        );
        $('#gallery-select-area :input').prop('disabled', false);
        $('#gallery-input-area :input').prop('disabled', false);
        $('#fileupload-area :input').prop('disabled', false);
      },
      progressall: function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        $('#progress .progress-bar').css(
            'width',
            progress + '%'
        );
      },
      submit: function (e, data) {
        handleGalleryChange();
        $('#gallery-select-area :input').prop('disabled', true);
        $('#gallery-input-area :input').prop('disabled', true);
        $('#fileupload-area :input').prop('disabled', true);

        $(document).unbind('click', hideOverlays);
      }
  }).prop('disabled', !$.support.fileInput)
      .parent().addClass($.support.fileInput ? undefined : 'disabled');

  var g_imagesToDelete = []

  function updateDeleteConfirmButton() {
    if (g_imagesToDelete.length) {
      $('#delete-btn-overlay').show('fade', g_speed);
      $('#confirm-delete-btn').click( confirmDelete );
    } else {
      $('#delete-btn-overlay').hide('fade', g_speed);
    }
  }

  function clickDeleteCheckbox() {
      if ($(this).is(':checked')) {
          g_imagesToDelete.push($(this).attr('id'));
      } else {
          var index = g_imagesToDelete.indexOf($(this).attr('id'));
          if (index > -1) {
            g_imagesToDelete.splice(index, 1);
          }
      }

      updateDeleteConfirmButton();
  }

  function updateDeleteButton(enable) {
    if (enable) {
        $('#delete-btn').switchClass('btn-primary', 'btn-warning', g_speed);
        $('#delete-btn').text('Cancel deletion');
    } else {
        $('#delete-btn').switchClass('btn-warning', 'btn-primary', g_speed);
        $('#delete-btn').text('Delete images');
    }
  }

  function enableDelete(enable) {
    updateDeleteButton(enable);

    g_imagesToDelete = []
    updateDeleteConfirmButton();

    $('.gallery-image-right').each( function() {
        if ($(this).find('.glyphicon-ok').length) {
          $(this).parent('div.row').remove();
          return;
        }

        $(this).find('.glyphicon-warning-sign').each( function() {
          $(this).find('.glyphicon-warning-sign').remove();
        });

        if (enable) {
            $(this).append('<div class="delete-confirmation checkbox"><label>' +
                           '<input type="checkbox" value="0">' +
                           '<i class="glyphicon glyphicon-remove"></i></label></div>');
            $(this).find('input').each( function() { $(this).click( clickDeleteCheckbox ); });
        } else {
            $(this).find('div.delete-confirmation').each( function() { $(this).remove(); });
        }
    });
  }

  function finishDelete() {
      enableDelete(false);
  }

  $('#delete-btn').click( function() {
      if ($('#delete-btn').hasClass('btn-primary')) {
        enableDelete(true);
      } else {
        enableDelete(false);
      }
  });

  function confirmDelete() {
    $('div.gallery-image-right').each( function() {
        var url = null;
        var _this = $(this);

        if (_this.find('input').is(':checked')) {
          _this.find('div.delete-confirmation').each( function() { $(this).remove(); });
          _this.append('<i class="glyphicon glyphicon-refresh delete-result"></i>');
          url = '/delete/' + _this.attr('id');
        } else {
          _this.find('div.delete-confirmation').each( function() { $(this).remove(); });
        }

        $('#delete-btn-overlay').hide('fade', g_speed);
        updateDeleteButton(false);

        if (!url)
            return;

        $.ajax({
          url: url,
          type: 'DELETE',
          success: function(data) {
            if (data) {
              _this.find('i').each( function() { $(this).remove(); });
              _this.append('<i class="glyphicon glyphicon-ok delete-result"></i>');
              window.setTimeout( finishDelete, 3000 );
            }
          },
          error: function(error) {
            console.log(error);
            _this.find('i').each( function() { $(this).remove(); });
            _this.append('<i class="glyphicon glyphicon-warning-sign delete-result"></i>');
          }
        });
    });
  }
});
