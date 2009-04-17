#!/usr/bin/python
from __future__ import with_statement

import web
from datetime import datetime

from backend import state, search, engine, online
from html import *
import render_post

from frontend.log import *



log_dbg("Initializing graypages . . .")

render = web.template.render('templates/')

class LoggedIn: #for mixing in
  def auth(self):
    cookies = web.cookies()
    try:
      if not self.ctx.has_key('name'):
        self.ctx['name'] = cookies['name']
      name = self.ctx['name'] #okay, it's set properly now
      try: #now get the UID
        self.ctx['uid'] = texas.get_uid_from_name(name)
      except: #TODO: be specific
        raise CantAuth("Unknown username: '" + name +"'")

      ticket = cookies['ticket_for_' + name]
    except KeyError, e:
      raise CantAuth("Not logged in.")
    if not texas.check_ticket(self.ctx['uid'], ticket):
      raise CantAuth("Invalid ticket.")
    web.setcookie('name', name, expires=3600*24*90)
    web.setcookie('ticket_for_'+name, ticket, expires=3600*24*90)

  def logout(self):
    if self.ctx.has_key('name'):
      name = self.ctx['name']
    else:
      try:
        name = cookies['name']
      except KeyError, e:
        pass #Not logged in at all?
    web.setcookie('name', '', expires=-1)
    web.setcookie('ticket_for_'+name, '', expires=-1)


def emit_post(post, uid=None, terms=None, extras={}, expose=True):
  #TODO: maybe, instead of this expose/non-expose crud, we should put
  #in the whole article at first, stash the summary somewhere else,
  #and just have JS replace as appropriate (and make replace do
  #animation universally).  Advantage: almost all page transitions are
  #controled by replace='' parameters...
  exp_ctrl = ' exposed' if expose else ''

  all_extras = {'score': post.broad_support, 'id': post.id}
  all_extras.update(extras)

  
  with div(info={'id': str(post.id)}, css='post', c_id='post') as ret_val:
    with js_link(fn=dummy, css='dismisser'):
      img(alt='dismiss this entry', src='/static/x-icon.png')
    h3()
    with div(css='sidebar'):
      with div(c_id='sidebar_summary', css='j_summary', expose=expose):
        txt("(")
        with js_link(fn=dummy): txt("expand")
        txt("|")
        with link(service=dummy): txt("page")
        txt(")")
      with div(c_id='sidebar_content', css='j_content', expose=expose):
        txt("(")
        with js_link(fn=dummy): txt("contract")
        txt("|")
        with link(service=dummy): txt("page")
        txt(")"), br()
      txt("TODO ago"), br()
      for k, v in all_extras.items():
        with bold():
          txt(k)
        txt(": "), txt(str(v))
      with div(css='sidebarsection'):
        txt("TODO notes")
    with div(): #post body
      with div(c_id='summary', css='j_summary postbody', expose=expose):
        txt("Fit nasal purse")
      with div(c_id='content', css='j_content postbody', expose=expose):
        txt(post.raw())
        if uid != None:
          with div(c_id='tools', css='tools'):
            if texas.voted_for(uid, post.id):
              txt("by ")
              with link(service=dummy):
                img(alt='', src='/static/user.png')
                texas.get_user(post.uid).name
              button(service=dummy, label='Good quote', replace='post')
              if terms != None:
                button(service=dummy, label='Worth the read for "%s"'%terms,
                       replace='tools')
            else:
              button(service=dummy, label='Worth the read', replace='tools')
    div(style='clear: both;')
  return ret_val.emit()
        

#   if uid == None:
#     tools_block = ""
#   else:
#     author_name = texas.get_user(post.uid).name
    
#     if texas.voted_for(uid, post.id):
#       if terms != None:
#         terms_ctrl = button(service=dummy, label='Worth the read for "%s"' % terms, replace='post')
#       else:
#         terms_ctrl = ""
#       tools_block = div(c_id='tools')(
#         "by ", link(service=dummy)(
#           img(alt='', src='/static/user.png'), author_name),
#         button(service=dummy, label='Good quote', replace='post'),
#         terms_ctrl)
#     else:
#       tools_block = "TODO voter block"

        
#   return str(
#     div(info={'id': str(post.id)}, style='clear: both;', css='post', c_id='post')(
#       js_link(fn=dummy, css='dismisser')(
#         img(alt='dismiss this entry', src='/static/x-icon.png/')),
#       h3()("Claim: ", span(c_id='claim')(post.claim)),
#       div(css='sidebar')(
#         div(c_id='sidebar_summary', css='j_summary', expose=expose)(
#           "(", js_link(fn=dummy)("expand"), " | ",
#              link(service=dummy)("page"), ")"),
#         div(c_id='sidebar_contents', css='j_content', expose=expose)(
#           div(css='sidebarsection')(
#             "(", js_link(fn=dummy)("contract"), " | ",
#                link(service=dummy)("page"), ")", br(),
#           "TODO ago", br(),
#           ' '.join([ k + ": " + str(v)  for k,v in all_extras.items()]),
#           "TODO extras"),
#           div(css='sidebarsection')(
#             "TODO notes")
#         ), #end of sidebar_contents
#       ), #end of sidebar
#       div(c_id='summary', css='j_summary postbody', expose=expose)(
#         "Fit nasal purse." ),
#       div(c_id='contents', css='j_content postbody', expose=expose)(
#         post.raw(), #TODO render more
#         tools_block),
#       div(style='clear: both;')))



urls = ('/favicon.ico', 'favicon',
        '/login', 'login',
        '/register', 'register',
        '/', 'default',
        '/users/(.+)/frontpage', 'frontpage',
        '/users/(.+)/history/(.+)', 'history',
        '/articles/(.+)/wtr', 'vote',
        '/articles/(.+)/for/(.+)/wtr', 'vote_term',
        '/articles/(.+)/callout', 'callout',
        '/articles/(.+)', 'article',
        '/users/(.+)/search', 'search_results',
        '/users/(.+)/compose', 'compose',
        '/admin/recluster', 'recluster')

#_texas_ is assigned (in _serve()_)to the state that we're concerned with.  In honor
#of Christine, 'casue I can't think of a better name
texas = state.the
search = texas.search


class login: #TODO: authenticate.  username or email address required, not both
  def GET(self):
    inp = web.input()
    if not inp.has_key('name'):
      print "give a name!"
      return
    name = inp.name
    uid = texas.get_uid_from_name(name)
    web.setcookie('name', name, expires=3600*24*90)
    ticket = texas.make_ticket(uid)
    web.setcookie('ticket_for_' + name, ticket, expires=3600*24*90)
    #web.seeother('/users/' + name + '/frontpage')
    print '<a href="/users/' + name + '/frontpage">'+name+'</a>'
  def POST(self):  #TODO: userify
    inp = web.input()
    try:
      texas.create_user(inp.name, inp.pwd, inp.email)
    except state.DataError, e:
      print 'Unable to create user:', e
      return
    print 'Welcome new user ' + inp.name

#TODO: should _cookie_session_ and _normal_style_ be classes?  I'm
#starting to think it doesn't really make sense.


class BitBucket:
  def write(self, s): pass

class normal_style:
  web.webapi.internalerror = web.debugerror
  
  def __init__(self):
    import time
    self.start = time.time()

  def package(self, sidebar, content, real_user=False, username=None, js_files=[], title='firegray'):
    import time
    print '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
<head><title>%s</title>
<link rel="stylesheet" type="text/css" href="/static/yb.css" />
<link rel="shortcut icon" href="/static/read.png" />
<script src="/static/jquery-1.2.6.min.js" type="text/javascript"></script>
''' % title
    for js in js_files:
      print '<script src="/static/%s" type="text/javascript"></script>' % js

    print '</head><body>'
    print render.sidebar_top(username)
    print sidebar
    print render.sidebar_bottom(real_user, username)
    print '<div class="stream">'
    print render.navbar(real_user, username)
    print content
    print '</div></body></html>'
    log_dbg('total service time: %f seconds' % (time.time() - self.start))

  
  def nav_wrap(self, content, username, cur_batch, front, fresh):
     #history doesn't make sense without a user
    if username == None: return content
    navver = (
       ('<a style="float: left" href="/users/%s/history/%d">older</a>' % (username, cur_batch-1))
      +(('<a style="float: right" href="/users/%s/history/%d">newer</a>' % (username, cur_batch+1))
        if (not front) else
        ('<a style="float: right" href="/users/%s/frontpage?fresh=yes">gather new articles</a>'
           % (username))))
    if not fresh:
      return ('<center><i>'
              +('You\'ve probably seen these articles already.  You can '
                if front else
                'You can also ')
              + '<a href="/users/%s/frontpage?fresh=yes">gather new articles</a>.</i></center>' % username
              + content + navver)
    return content + navver


class CantAuth(Exception):
  def __init__(self, msg):
    self.msg = msg

  def __call__(self):  #executable exceptions become pages?
    print '<html><head></head><body>' + msg + '</body></html>'

class IllegalAction(Exception):
  def __init__(self, msg):
    self.msg = msg

#Private, but non-sensitive activities are accessible with a cookie login
class cookie_session:
  #Returns the uid, if the user is logged in.  If the username is
  #provided (e.g., from a URL), try that one.  Otherwise, check the
  #cookies for the last session.  
  #
  #Require a proper login with a password before doing anything
  #serious/unreversable
  def uid_from_cookie(self, name_from_url=None):
    cookies = web.cookies()

    try:
      if name_from_url != None:
        username = name_from_url  
      else:
        username = cookies['name']
      try:
        uid = texas.get_uid_from_name(username)
      except: #username not recognized (rare -- mucking with cookies?)
        raise CantAuth("User name '" + username+"' not recognized.")
      ticket = cookies['ticket_for_' + username]
    except KeyError: #name missing (cookies cleared?) or ticket missing (rare)
      raise CantAuth("Not logged in.")
    if texas.check_ticket(uid, ticket):
      web.setcookie('name', username, expires=3600*24*90) #sets identity
      #after three months of inactivity, you get logged out
      return uid
    else: #ticket invalid (rare -- mucking with cookies?)
      raise CantAuth("Invalid ticket.")
  
  def logout(self, name_from_url=''):
    if len(name_from_url) > 0:
      name = name_from_url
    else:
      try:
        name = web.cookies()['name']
      except KeyError:
        raise CantAuth("Not logged in.")
      
    web.setcookie('name', '[invalid]', expires=-1) #nuke the cookie
    web.setcookie('ticket_for_' + name, '[invalid]', expires=-1)

class default(cookie_session):
  def GET(self):
    uid = self.uid_from_cookie()
    web.seeother('/users/' + username + "/frontpage")

class history(cookie_session, normal_style):
  def GET(self, username, pos):
    uid = self.uid_from_cookie(username) 
    user = texas.get_user(uid)
    
    if(pos == 'latest'):
      pos = user.current_batch-1 #making it an integer now
    else:
      pos = int(pos)

    content = ''
    posts = texas.get_history(uid, pos)
    for post in posts:
      content += emit_post(post, uid)

    if len(posts) == 0:
      content = '<i>You don\'t seem to have history in the requested range.</i>'

    sidebar = render.ms_sidebar([texas.get_post(wtr) for wtr in texas.recent_votes(uid, 4)])
    self.package(sidebar,
        self.nav_wrap(content, username, pos,
                      pos == user.current_batch-1, False),
        uid < 10, username, js_files=['citizen.js'])
    

#/users/<username>/frontpage
class frontpage(cookie_session, normal_style):
  def GET(self, username):
    i = web.input()
    if(not i.has_key('fresh')):
      web.seeother('/users/'+username+'/history/latest')
      return
    
    uid = self.uid_from_cookie(username) #TODO: handle error

    user = texas.get_user(uid)
    user_cluster = user.cid
    content = ''

    if(i.has_key('articles')):
      article_count = int(i['articles'])
      if article_count < 1 or article_count > 25:
        article_count = 6
    else:
      article_count = 6
    
    posts = online.gather(user, texas)[0:article_count]
    for i, post in enumerate(posts):
      texas.add_to_history(uid, post.id, user.current_batch, i)
      content += emit_post(post, uid)

    if len(posts) == 0:
      content = '<i>We\'re out of articles for you at the moment.  If you\'re halfway normal, there should be some here for you soon.</i>'
    else:
      texas.inc_batch(user) #batches seperate the history into pages



    sidebar = render.ms_sidebar([texas.get_post(wtr) for wtr in texas.recent_votes(uid, 4)])

    self.package(sidebar,
        self.nav_wrap(content, username, user.current_batch, True, True),
        uid < 10, username, js_files=['citizen.js'])


class article(cookie_session, normal_style):
  def GET(self, pid):
    pid = int(pid)
    post = texas.get_post(pid, content=True)
    try:
      uid = self.uid_from_cookie(None)
      content = emit_post(post, uid, expose=True)
      real = uid > 10
    except CantAuth:
      username = None
      real = False
      content = emit_post(post, None, expose=True)

    self.package('', #TODO: make a special sidebar
                 content,
                 real, username, js_files=['citizen.js'])

class compose(cookie_session, normal_style):
  def GET(self, username): #composition page

    uid = self.uid_from_cookie(username)    

    self.package(render.c_sidebar(), render.c_body(), uid < 10, username, js_files=['quicktags.js', 'editor.js'])

  def POST(self, username): #submit a post
    i = web.input()
    uid = self.uid_from_cookie(username)
    #TODO: we need to deal with pids in posts.  And record the author.
    pid = texas.create_post(uid, i.claim, i.posttext)
    web.seeother('/articles/' + str(pid))

class search_results(cookie_session, normal_style):
  def GET(self, username):
    inp = web.input()
    terms = inp.search

    uid = self.uid_from_cookie(username) #TODO error handling
    user = texas.get_user(uid)

    if inp.local:
      results = search.local_search(user.cid, terms, inp.recent)
    else:
      results = search.global_search(terms, inp.recent)

    content = ""
    for i, result in enumerate(results):
      texas.add_to_history(uid, result.post.id, user.current_batch, i)
      content += emit_post(result.post, uid, terms, {"score": result.score})
      
    sidebar = render.search_sidebar(inp.local)
    self.package(sidebar, content, uid < 10, username, js_files=['citizen.js'])
    
class vote(cookie_session):
  def POST(self, pid_str):
    i = web.input()
    pid = int(pid_str)
    post = texas.get_post(pid)
    uid = self.uid_from_cookie()
    username = texas.get_user(uid).name
    texas.vote(uid, pid)
    if i.has_key('term'):
      texas.add_term(uid, pid, i['term'])
    
    author_uid = post.uid
    author_name = texas.get_user(author_uid).name
    if i.has_key('ajax'):
      print render.vote_result(texas.get_post(pid), username, author_name, author_uid, None)
      #no extra term is possible in the context of just having voted
    else:
      print "TODO: wrap a simple js-less version"
      #web.seeother('/articles/' + str(pid)) #no JS?  redirect to view the whole article

class callout(cookie_session):
  def POST(self,  pid_str):
    pid = int(pid_str)
    uid = self.uid_from_cookie()

    if not texas.voted_for(uid, pid):
      raise IllegalAction("You may only make a callout on an article that you've voted for.")

    #TODO: figure out somewhere to put the callout logic
    

class recluster:
  def GET(self):
    cluster_assignments = engine.cluster_by_votes(texas)
    texas.applyclusters(cluster_assignments)
    print 'Clusters reassigned'
    #TODO throw in some diagnostic
    #for uid in texas.users: print texas.users[uid]

class favicon:
  def GET(self):
    print open('static/fg.ico', 'r').read()
    
def not_found():
  print render.not_found()

def config(wsgifunc):
  bb = BitBucket()
  def ret_val(env, start_resp):
    env['wsgi.errors'] = bb
    return wsgifunc(env, start_resp)
  return ret_val
    
def serve():
  web.run(urls, globals(), web.reloader, config)
  
if __name__ == "__main__":
  serve()

