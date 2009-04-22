from backend.state import State
from datetime import timedelta, datetime
import web

render = web.template.render('templates/')
    
def show(post, vote_result=None, username=None, term=None, extras={}, expose=False):
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


    return render.post(pid, "exposed" if expose else "",
                       post.claim, callout, content, 
                       render_timedelta(age),
                       extras_rendered, notes_rendered,
                       vote_result, username, term)
