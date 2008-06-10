function dismiss(id) {
  var post = document.getElementById("post"+id);
  post.parentNode.removeChild(post);
  //TODO notify server, so it won't be displayed on future page loads
}

function expose(id) { //TODO: support earlier browsers
  document.getElementById('summary'+id).style.display = 'none';
  document.getElementById('contents'+id).style.display = 'inline';
}

function shrink(id) { //TODO: support earlier browsers
  document.getElementById('summary'+id).style.display = 'inline';
  document.getElementById('contents'+id).style.display = 'none';
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
