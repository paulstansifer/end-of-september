// JS QuickTags version 1.2
//
// Copyright (c) 2002-2005 Alex King
// http://www.alexking.org/
//
// Licensed under the LGPL license
// http://www.gnu.org/copyleft/lesser.html
//
// **********************************************************************
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
// **********************************************************************

// Trimmed down to just the part we need to use.  
// Also, rewrote it some for more generality.  --PS 2008
// The original is at http://alexking.org/projects/js-quicktags/demo/js_quicktags.js

function edSurroundContent(myField, beforeSel, afterSel) {
	//IE support
  if (document.selection) {
    myField.focus();
    sel = document.selection.createRange();
    if(sel.text.length > 0) {
      sel.text = beforeSel + sel.text + afterSel;
      myField.focus();
    }
  }
	//MOZILLA/NETSCAPE support
  else if (myField.selectionStart || myField.selectionStart == '0') {
    var startPos = myField.selectionStart;
    var endPos = myField.selectionEnd;
    if(startPos != endPos) {
      var scrollTop = myField.scrollTop;
      myField.value = myField.value.substring(0, startPos)
        + beforeSel
        + myField.value.substring(startPos, endPos)
        + afterSel
        + myField.value.substring(endPos, myField.value.length);
      myField.focus();
      myField.selectionStart = endPos + beforeSel.length + afterSel.length;
      myField.selectionEnd = endPos + beforeSel.length + afterSel.length;
      myField.scrollTop = scrollTop;
    }
  } else {
    //TODO: fallback?
    /*
		myField.value += myValue;
		myField.focus();
     */
  }
}

function edFollowCursor(myField, markup) {
  //IE support
  if (document.selection) {
    myField.focus();
    sel = document.selection.createRange();
    sel.text =  sel.text + markup;
    myField.focus();
  }
  //MOZILLA/NETSCAPE support
  else if (myField.selectionStart || myField.selectionStart == '0') {
    var startPos = myField.selectionStart;
    var endPos = myField.selectionEnd;
    var scrollTop = myField.scrollTop;
    myField.value = myField.value.substring(0, startPos)
      + myField.value.substring(startPos, endPos)
      + markup
      + myField.value.substring(endPos, myField.value.length);
    myField.focus();
    myField.selectionStart = endPos + beforeSel.length + afterSel.length;
    myField.selectionEnd = endPos + beforeSel.length + afterSel.length;
    myField.scrollTop = scrollTop;
  } else {
     myField.value += markup;
     myField.focus();
  }
}
