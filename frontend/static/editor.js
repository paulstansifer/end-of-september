function markup(lhs, rhs, purpose) {
  edSurroundContent(composer.posttext, lhs, rhs);
  document.getElementById('editor_explain').innerHTML =
    "<div class='notice'>To make something " + purpose + ", mark it up " + lhs + "like this" + rhs +"</div><br/>";
}

var footnote_number = 1;
function footnote() {
  edSurroundContent(composer.posttext, "", "[" + footnote_number++ + "]");
}

var composer = document.getElementById('comp');

function enlarge() {
  //composer = document.getElementById('comp');
  var elt = document.getElementById('comp').posttext;
  var cursize = parseInt(elt.getAttribute('rows'));
  moving_enlarge(cursize, 6);
}
function moving_enlarge(cursize, amt) {
  var elt = composer.posttext;
  if(3 > amt) {
    elt.setAttribute('rows', cursize + amt);
  } else {
    elt.setAttribute('rows', cursize + 2);
    setTimeout("moving_enlarge("+cursize+"+2, "+amt+"-2)", 70);
  }
}

//TODO:  Make this fancier, putting stuff where the cursor is
//or maybe there's an easier way?
function add_stuff(main, footnote) {
  composer.posttext.value += main;
  composer.footnotes.value += footnote;
}
