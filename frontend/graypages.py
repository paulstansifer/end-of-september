#!/usr/bin/python
# $Id: graypages.py 100 2008-04-11 00:34:48Z paul $
import web
from datetime import datetime

from state import State
from state_filler import populate_state
import engine
import render_post
import online

render = web.template.render('templates/')

urls = ('/favicon.ico', 'favicon',
        '/login', 'login',
        '/register', 'register'
        '/', 'default',
        '/users/(.*)/frontpage', 'frontpage',
        '/users/(.*)/compose', 'compose',
        '/users/(.*)/vote/wtr(.*)', 'vote',
        '/admin/recluster', 'recluster')

# Create a new page state object
state = State()

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
  def package(self, sidebar, content, real_user, username, js_files=[], title='firegray'):
    print '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
<head><title>%s</title>
<link rel="stylesheet" type="text/css" href="/static/yb.css" />
<link rel="shortcut icon" href="/static/read.png" />''' % title
    for js in js_files:
      print '<script src="/static/%s" type="text/javascript" />' % js

    print "</head><body>"
    print render.sidebar_top(username)
    print sidebar
    print render.sidebar_bottom(real_user, username)
    print '<div class="stream">'
    print render.navbar(real_user, username)
    print content
    print "</div></body></html>"


#Private, but non-sensitive activities are accessible with a cookie login
class cookie_session:
  #Returns the uid, if the user is logged in.  If the username is
  #provided (e.g., from a URL), try that one.  Otherwise, check the
  #cookies for the last session
  #
  #Require a proper login with a password before doing anything
  #serious/unreversable
  def get_uid_from_cookie(self, name_from_url=''):
    try:
      cookies = web.cookies()
      
      if len(name_from_url) > 0:
        username = name_from_url  
      else:
        username = cookies['name']
      uid = state.get_uid_from_name(username)
      if uid == None:
        web.seeother('/must_login') #TODO
        return None
      ticket = cookies['ticket_for_' + username]
    except KeyError:
      #TODO: we probably want some kind of appropriate error message
      web.seeother('/must_login') #TODO: we want to stop the rest of rendering from happening
      return None
    
    if state.check_ticket(uid, ticket):
      web.setcookie('name', username, expires=3600*24*90)
      #after three months of inactivity, you get logged out
      return uid
    else:
      return None
  
  def logout(self):
    web.setcookie('name', '', expires=-1) #nuke the cookie

class default(cookie_session):
  def GET(self):
    uid = self.get_uid_from_cookie()
    web.seeother('/users/' + state.get_user(uid).name + "/frontpage")
    

class frontpage(cookie_session, normal_style):
  def GET(self, username):
    web.webapi.internalerror = web.debugerror

    uid = self.get_uid_from_cookie(username)
    if uid is None:
      web.seeother('/login') #FIXME: handle error.
      return

    user = state.get_user(uid)
    user_cluster = user.cid
    content = ''

    #recommendations = engine.recommend_for_cluster(state, user_cluster)
    posts = online.gather(user, state)[0:6] #TODO: retirement
    for post in posts:
      content += '''<div class="post" id="post%d">
      <a href="javascript:dismiss(%d)" class="dismisser">
      <img alt="dismiss" src="/static/x-icon.png" /> </a>''' % (post.id, post.id)
      content += render_post.render(post, username, state.voted_for(uid, post.id), render)
      content += "</div>"

    sidebar = render.ms_sidebar()
    self.package(sidebar, content, uid < 10, username, js_files=['citizen.js'])

class compose(cookie_session, normal_style):
  def GET(self, username): #composition page
    web.webapi.internalerror = web.debugerror

    uid = self.get_uid_from_cookie(username)    

    self.package(render.c_sidebar(), render.c_body(), uid < 10, username, js_files=['quicktags.js', 'editor.js'])

  def POST(self, username): #submit a post
    i = web.input()
    uid = self.get_uid_from_cookie(username)
    #TODO: we need to deal with pids in posts.  And record the author.
    state.set_post(uid, i.claim, i.posttext)
    web.seeother('/users/' + username + '/frontpage')

    
class vote(cookie_session):
  def PUT(self, user, pid_str):
    pid = int(pid_str)
    web.webapi.internalerror = web.debugerror
    uid = self.get_uid_from_cookie(user)
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
