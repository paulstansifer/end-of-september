from state import State
from datetime import timedelta, datetime

def render_timedelta(td):
  seconds = td.seconds % 60
  minutes = (td.seconds // 60) % 60
  hours = td.seconds // (60*60)
  days = td.days % 365
  
  if(td < timedelta(0)):
    return "The FUTURE!"

  ret_val = ""
  if td < timedelta(0, 60*4): #short enough that we care about seconds
    if seconds == 1:
      ret_val = "1 second"
    else:
      ret_val = str(seconds) + " seconds"
          
  if td < timedelta(0, 60*60*4) and td > timedelta(0,60): #short enough that we care about minutes
    if len(ret_val) > 0:
      ret_val = ", " + ret_val
    if minutes == 1:
      ret_val = "1 minute" + ret_val
    else:
      ret_val = str(minutes) + " minutes" + ret_val

  if td < timedelta(3) and td > timedelta(0,60*60): #short enough that we care about hours
    if len(ret_val) > 0:
      ret_val = ", " + ret_val
    if hours == 1:
      ret_val = "1 hour" + ret_val
    else:
      ret_val = str(hours) + " hours" + ret_val
  
  if td > timedelta(1):
    if len(ret_val) > 0:
      ret_val = ", " + ret_val
    if hours == 1:
      ret_val = "1 day" + ret_val
    else:
      ret_val =  str(days) + " days" + ret_val
  
  return ret_val
    

def render(post, render, vote=None, username=None, term=None, extras={}):
    claim = post.claim
    age = datetime.now() - post.date_posted
    callout = 'I think you\'re pretty sexy, but I hate it when you talk.'
    raw = post.raw()
    
    content = raw.replace(callout, callout+"<div class='quote'>" + callout + "</div>", 1)

    
    #TODO: do better
    content = content.replace('[/', '<i>').replace('/]', '</i>').replace('[*', '<b>').replace('*]','</b>')
    #it might be best just to make a little compiler in bison.  It could handle the callouts, too.

    pid = str(post.id)
    notes_rendered = """<sup>a</sup> <a href='http://en.wikipedia.org/wiki/Pet_eye_remover'>[wikipedia]</a><br />
    <sup>b</sup> <a href='http://en.wikipedia.org/wiki'>[wikipedia]</a><br />
    <sup>c</sup> Technically, this isn't true.<br />
    <sup>d</sup> <a href='http://www.youtube.com/watch?v=eBGIQ7ZuuiU'>[youtube]</a><br />
    <sup>e</sup> If you squint at it. <br />"""

    extras_rendered = '';
    for (k, v) in extras.iteritems():
      extras_rendered += "<b>" + k + "</b>: " + str(v) + "<br/>"

    if vote == True:
      vote_result_rendered = render.vote_result(post.id)
    else:
      vote_result_rendered = None

    return render.post(pid, 'inline', 'none', post.claim, callout,
                       content, render_timedelta(age),
                       extras_rendered, notes_rendered,
                       vote_result_rendered, username, term)
