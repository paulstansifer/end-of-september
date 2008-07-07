import re
import state


class NoLuck(Exception):
  def __init__(self, msg):
    self.msg = msg

#We trust the HTMLification, formatting, rendering, selecting process to at least preserve these
sep_expr = r'[^\w,.]+' #chunks of meaningful text, corresponding approximately to words
seperator = re.compile(sep_expr, re.UNICODE)

def _locate_callout(text, callout):
  locator = sep_expr.join(
    [word.replace(r'.', r'\.') #we want to look for these in a regex
     for word in seperator.split(callout)]) #words in our callout
  match = re.search(locator, text) #look for the thing the user called out
  if match == None: raise NoLuck("Can't find the callout -- user selected wrong text?")
  return match.span()
  

def add_callout(callout_raw, uid, pid):
  _locate_callout(state.get_post(pid. True).raw,
                  callout_raw)
