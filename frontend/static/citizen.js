var inFlight = 0;

$(document).ready(function() {
    $(".j_content").not(".exposed").hide();
    $(".j_summary").not(".exposed").show();

    //$(".dismisser").show();
    //on consideration, what good does this do?  --PS

    $("#loading").bind("ajaxSend", function() {
        if(inFlight++ == 1) {
          $(this).show();
        }
      }).bind("ajaxStop", function() {
        if(inFlight-- == 0) {
          $(this).hide();
        }
      });

    $.ajaxSetup( {
      timeout: 4000, //ms
      dataType: 'html'
    });  
});


function dismiss(id) {
  //var post = document.getElementById("post"+id);
  //post.parentNode.removeChild(post);
  $("#post"+id).hide("slow");
  //TODO notify server, so it won't be displayed on future page loads
}

var slam_quick = 100;

function expose(id) { //TODO: support earlier browsers
  $("#summary"+id).slideUp(slam_quick);
  $("#sidebar_summary"+id).slideUp(slam_quick, function() {
      $("#content"+id).slideDown("slow");
      $("#sidebar_content"+id).slideDown("slow");
    });
}

function shrink(id) { //TODO: support earlier browsers
  $("#sidebar_content"+id).slideUp("slow");
  $("#content"+id).slideUp("slow", function() {
      $("#summary"+id).slideDown(slam_quick);
      $("#sidebar_summary"+id).slideDown(slam_quick);
    });
}



function callout(id, status_div) {
  txt = '';
  if(window.getSelection) {
    txt = window.getSelection();
  } else if (document.getSelection) {
    txt = document.getSelection();
  } else if (document.selection) {
    txt = document.selection.createRange().text;
  }
  if(txt == null || txt == '') {
    $('#'+status_div).hide().html(
      "Select a quotation from the article first to call it out.")
      .slideDown('fast');
  }
  //var req = ajax("/articles/"+id+"/callout?text="+escape(txt));
}

function add_recent_wtr(id) {
   $('#recentwtr').prepend("<li><a style='display:none' class='listedlink'" 
     +"href='/articles/'+id>"+ $("#claim"+id).text() + "</a></li>")
     .children(':first').children(':hidden').fadeIn('slow');
}

function ajax_replace(id, url, status_div, method) {
  $('#'+status_div).hide().html('Working...').slideDown('fast');
  $.ajax({
    url: url+'?format=inner_xhtml', dataType: 'html', type: method,
    success: function(data, textstatus) {
        $('#'+id).hide().html(data).fadeIn('normal');
        //$('#'+status_div).slideUp('slow'); //done!
        $('#recentwtr').prepend("<i>STATUS: "+textstatus+"</i>");
        //callback();
      },
    error: function(request, textstatus, error) {
        alert(textstatus);
        alert(error);
        if(textstatus == 'timeout') {
          $('#'+status_div).html('Timeout trying to contact server.');
        } else {
          $('#'+status_div).html('Internal error talking to server.'+textstatus);
        }
      }
    });
}

function voteon(id, username, term) {
  url = $('#wtr'+id).attr('action') + '&ajax=inline';
  $("#status"+id).html('');
  $.ajax({
    url: url,
    dataType: 'html', type: 'POST',
    success: function(data, textstatus) {
        $('#wtr'+id).hide().html(data).fadeIn('normal');
        $('#recentwtr').prepend(
           "<li><a style='display:none' class='listedlink' href='/articles/"
           +id+"'>"+ $("#claim"+id).text() + "</a></li>")
          .children(':first').children(':hidden').fadeIn('slow');
      },
    error: function(data, textstatus) {
        if(textstatus == 'timeout') {
          $('#status'+id).html('<em>Timeout trying to contact to server.</em>');
        } else {
          $('#status'+id).html('<em>Internal error talking to server.</em>');
        }
      }
  });
}
