var inFlight = 0;

$(document).ready(function() {
    $(".j_content").not(".expose").hide();
    $(".j_summary").not(".expose").show();

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
      $("#contents"+id).slideDown("slow");
      $("#sidebar_contents"+id).slideDown("slow");
    });
}

function shrink(id) { //TODO: support earlier browsers
  $("#sidebar_contents"+id).slideUp("slow");
  $("#contents"+id).slideUp("slow", function() {
      $("#summary"+id).slideDown(slam_quick);
      $("#sidebar_summary"+id).slideDown(slam_quick);
    });
}


function callout(id) {
  txt = '';
  if(window.getSelection) {
    txt = window.getSelection();
  } else if (document.getSelection) {
    txt = document.getSelection();
  } else if (document.selection) {
    txt = document.selection.createRange().text;
  }
  //var req = ajax("/articles/"+id+"/callout?text="+escape(txt));
}

function voteon(id, username) {
  $("#status"+id).html('');
  $.ajax({
    url: '/articles/'+id+'/wtr?just_result=yes',
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
