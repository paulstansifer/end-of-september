#!/usr/bin/python
# $Id: graypages.py 100 2008-04-11 00:34:48Z paul $
import web
from datetime import datetime

import state, search
from state_filler import populate_state
import engine
import render_post
import online

print "Initializing graypages . . ."

render = web.template.render('templates/')

urls = ('/favicon.ico', 'favicon',
        '/login', 'login',
        '/register', 'register',
        '/', 'default',
        '/users/(.*)/frontpage', 'frontpage',
        '/view/(.*)', 'article',
        '/users/(.*)/search', 'search_results',
        '/users/(.*)/compose', 'compose',
        '/users/(.*)/vote/wtr(.*)', 'vote',
        '/admin/recluster', 'recluster')

# get the system state clearinghouse
state = state.the
search = search.the

web.webapi.internalerror = web.debugerror

class login: #TODO: authenticate.  username or email address required, not both
  def GET(self):
    inp = web.input()
    if not inp.has_key('name'):
      print "give a name!"
      return
    name = inp.name
    uid = state.get_uid_from_name(name)
    web.setcookie('name', name, expires=3600*24*90)
    ticket = state.make_ticket(uid)
    web.setcookie('ticket_for_' + name, ticket, expires=3600*24*90)
    #web.seeother('/users/' + name + '/frontpage')
    print '<a href="/users/' + name + '/frontpage">'+name+'</a>'
  def PUT(self):
    pass


class normal_style:
  def package(self, sidebar, content, real_user=False, username=None, js_files=[], title='firegray'):
    print '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
<head><title>%s</title>
<link rel="stylesheet" type="text/css" href="/static/yb.css" />
<link rel="shortcut icon" href="/static/read.png" />''' % title
    for js in js_files:
      print '<script src="/static/%s" type="text/javascript"></script>' % js

    print "</head><body>"
    print render.sidebar_top(username)
    print sidebar
    print render.sidebar_bottom(real_user, username)
    print '<div class="stream">'
    print render.navbar(real_user, username)
    print content
    print "</div></body></html>"


class CantAuth(Exception):
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
      uid = state.get_uid_from_name(username)
      if uid == None: #username not recognized (rare -- mucking with cookies?)
        raise CantAuth("User name '" + username+"' not recognized.")
      ticket = cookies['ticket_for_' + username]
    except KeyError: #name missing (cookies cleared?) or ticket missing (rare)
      raise CantAuth("Not logged in.")
    if state.check_ticket(uid, ticket):
      web.setcookie('name', username, expires=3600*24*90)
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
    web.seeother('/users/' + state.get_user(uid).name + "/frontpage")

def post_wrap(post, username, uid, term=None, extras={}):
  info = {'score': post.broad_support, 'id': post.id }
  info.update(extras)
  return ('''<div class="post" id="post%d">
    <a href="javascript:dismiss(%d)" class="dismisser">
    <img alt="dismiss" src="/static/x-icon.png" /> </a>'''
          % (post.id, post.id)
      + render_post.render(post, render,
                           vote=state.voted_for(uid, post.id),
                           username=username, term=term, extras=info)
      + "</div>")

class frontpage(cookie_session, normal_style):
  def GET(self, username):
    web.webapi.internalerror = web.debugerror

    uid = self.uid_from_cookie(username)
    if uid is None:
      web.seeother('/login') #FIXME: handle error.
      return

    user = state.get_user(uid)
    user_cluster = user.cid
    content = ''

    #recommendations = engine.recommend_for_cluster(state, user_cluster)
    posts = online.gather(user, state)[0:6] #TODO: retirement
    for post in posts:
      content += post_wrap(post, user.name, uid)

    sidebar = render.ms_sidebar()
    self.package(sidebar, content, uid < 10, username, js_files=['citizen.js'])

class article(cookie_session, normal_style):
  def GET(self, pid):
    pid = int(pid)
    post = state.get_post(pid, content=True)
    try:
      uid = self.uid_from_cookie(None)
      username = state.get_user(uid).name
      real = uid < 10
      content = render_post.render(post, render,
                                   state.voted_for(uid, pid),
                                   username)
    except CantAuth:
      username = None
      real = False
      content = render_post.render(post, render)

    self.package(render.ms_sidebar(), #TODO: make a special sidebar
                 '<div class="post" id="post%d">' + content + '</div>',
                 real, username, js_files=['citizen.js'])

class compose(cookie_session, normal_style):
  def GET(self, username): #composition page
    web.webapi.internalerror = web.debugerror

    uid = self.uid_from_cookie(username)    

    self.package(render.c_sidebar(), render.c_body(), uid < 10, username, js_files=['quicktags.js', 'editor.js'])

  def POST(self, username): #submit a post
    i = web.input()
    uid = self.uid_from_cookie(username)
    #TODO: we need to deal with pids in posts.  And record the author.
    state.create_post(uid, i.claim, i.posttext)
    web.seeother('/users/' + username + '/frontpage')

class search_results(cookie_session, normal_style):
  def GET(self, username):
    
    i = web.input()
    terms = i.search

    uid = self.uid_from_cookie(username) #TODO error handling

    if i.local:
      results = search.local_search(state.get_user(uid).cid, terms, i.recent)
    else:
      results = search.global_search(terms, i.recent)

    content = ""
    for result in results:
      content += post_wrap(result.post, username, uid, result.term, {"score": result.score})
      
    sidebar = render.search_sidebar(i.local)
    self.package(sidebar, content, uid < 10, username, js_files=['citizen.js'])


    
class vote(cookie_session):
  def PUT(self, user, pid_str):
    pid = int(pid_str)
    web.webapi.internalerror = web.debugerror
    uid = self.uid_from_cookie(user)
    state.vote(uid, pid)
    print render.vote_result(state.get_post(pid))

class recluster:
  def GET(self):
    web.webapi.internalerror = web.debugerror

    cluster_assignments = engine.cluster_by_votes(state)
    state.applyclusters(cluster_assignments)
    print 'Clusters reassigned'
    #TODO throw in some diagnostic
    #for uid in state.users: print state.users[uid]

class favicon:
  def GET(self):
    print open('static/fg.ico', 'r').read()
    
def not_found():
  print render.not_found() #TODO: reduce irony by creating template

if __name__ == "__main__":
  web.run(urls, globals(), web.reloader)
