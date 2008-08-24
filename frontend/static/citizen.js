$(document).ready(function() {
    $(".j_content").not(".expose").hide("normal");
    $(".j_summary").not(".expose").show();

    //$(".dismisser").show();
    //on consideration, what good does this do?  --PS
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
  /*
  document.getElementById('summary'+id).style.display = 'none';
  document.getElementById('contents'+id).style.display = 'block';
  document.getElementById('sidebar_summary'+id).style.display = 'none';
  document.getElementById('sidebar_contents'+id).style.display = 'block';*/
}

function shrink(id) { //TODO: support earlier browsers
  $("#sidebar_contents"+id).slideUp("slow");
  $("#contents"+id).slideUp("slow", function() {
      $("#summary"+id).slideDown(slam_quick);
      $("#sidebar_summary"+id).slideDown(slam_quick);
    });

  /*
  document.getElementById('summary'+id).style.display = 'block';
  document.getElementById('contents'+id).style.display = 'none';
  document.getElementById('sidebar_summary'+id).style.display = 'block';
  document.getElementById('sidebar_contents'+id).style.display = 'none';
  */

}

function ajax(url) {
  var req;
  try{
    req = new XMLHttpRequest();
    } catch(e) {
    try{
      req = new ActiveXObject("Msxml2.XMLHTTP");
    } catch(e) {
      try{
        req = new ActiveXObject("Microsoft.XMLHTTP");
      } catch(e) {
        alert("Browser doesn't appear to support AJAX");
      }
    }
  }
  req.open("PUT",url,true)
  req.send(null);
  return req;
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
  var req = ajax("/users/"+username+"/vote/callout"+id+"?text="+escape(txt));
}

function voteon(id, username) {
  var form = document.getElementById("wtr"+id);
  var req = ajax("/users/"+username+"/vote/"+form.id);

  req.onreadystatechange = function(element) { 
    form.getElementsByTagName('div')[0].innerHMTL = "<em>"+req.readyState+"</em>";

    if(req.readyState==4) {
      if(req.status == 200 && req.responseText != null) {
        form.innerHTML = req.responseText;
      } else { //the 'div' thing is a hack
        form.getElementsByTagName('div')[0].innerHMTL = "<br /> <em>Failed to contact server</em>";
      }
    } else {
      document.getElementById('status'+id).innerHTML = "<em>Waiting for the server...</em>";
    }
  }
}
