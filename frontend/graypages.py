#!/usr/bin/python
from __future__ import with_statement

import web
from datetime import datetime

from backend import state, search, engine, online
from html import *
import js

import human_friendly

from frontend.log import *

log_dbg("Initializing graypages . . .")

render = web.template.render('templates/')


# A note about dc (doc context):

# It exists in two places: there's a hierarchy of it on the tags,
# added to by adding 'dc={...}' to a tag's arg list.  This is picked
# up by the url() classmethod of other Service s to which we are
# creating buttons or links.  There's also the dc of the current
# Service, which we feed to the root of the document, and is used by
# the service itself sometimes.


class UserTools:
  def issue_credentials(self):
    web.setcookie('name', self.dc['username'], expires=3600*24*90)
    ticket = texas.make_ticket(self.dc['uid'])
    web.setcookie('ticket_for_'+str(self.dc['uid']), ticket, expires=3600*24*90)
    
    

class ArticleTools: #for mixing in with Service
  def emit_vote_tools(self, post, voted_for):
    #vote_tools can occur without a post, so it needs ctxid, too.
    with div(dc={'ctxid': post.id, 'pid': post.id}, idc='tools', css='tools'):
      button(service=Vote, label='Worth the read', replace='tools',
             disabled=voted_for)
      if self.dc.has_key('terms'):
        terms = self.dc['terms']
        button(dc={'terms': terms}, service=Vote, replace='tools',
               label='... for "%s"' % self.dc['terms'])

      if voted_for:
        br()
        txt(human_friendly.render_timedelta(datetime.now()
                                            - post.date_posted))
        txt(" ago "); entity('mdash'); txt(" by ")
        with link(service=Dummy):
          img(alt='', src='/static/user.png')
          texas.get_user(post.uid).name
        button(service=Dummy, label='Good quote', replace='post')

      
  def emit_post(self, post, extras={}, expose=True):
    #TODO: maybe, instead of this expose/non-expose crud, we should put
    #in the whole article at first, stash the summary somewhere else,
    #and just have JS replace as appropriate (and make replace do
    #animation universally).  Advantage: almost all page transitions are
    #controled by replace='' parameters...
    exp_ctrl = ' exposed' if expose else ''

    all_extras = {'score': post.broad_support, 'id': post.id}
    all_extras.update(extras)

    
    with div(dc={'ctxid': post.id, 'pid': post.id}, css='post', idc='post', style='clear: both;'):
      with js_link(fn=dummy_js, css='dismisser'):
        img(alt='dismiss this entry', src='/static/x-icon.png')
      with h2():
        with span(css='posttitle'):
          #with span(style='font-weight: normal;'): txt("Claim: ")
          txt(post.claim)
          with js_link(fn=js.hide('content')): txt('hide')
#       with div(css='sidebar'):
#         with div(style='text-align: center; margin-bottom: 1em;'):
#           with div(idc='sidebar_summary', css='j_summary', expose=expose,
#                    child_sep=" | "):
#             with js_link(fn=dummy_js): txt("expand")
#             with link(service=Dummy): txt("page")
#           with div(idc='sidebar_content', css='j_content', expose=expose,
#                    child_sep=" | "):
#             with js_link(fn=dummy_js): txt("contract")
#             with link(service=Dummy): txt("page")
#         #for k, v in all_extras.items():
#         #  with bold(): txt(k)
#         #  txt(": "); txt(str(v))
#         txt("TODO notes")
      with div(): #post body
        with div(idc='summary', css='j_summary postbody', expose=expose):
          txt("Fit nasal purse")
        with div(idc='content', css='j_content postbody', expose=expose):
          txt(post.raw())
          if self.dc.has_key('uid'):
            self.emit_vote_tools(post, texas.voted_for(self.dc['uid'], post.id))
      div(style='clear: both;')
        
#######################################################
# urls = ('/favicon.ico', 'favicon',                  #
#         '/login', 'login',                          #
#         '/register', 'register',                    #
#         '/', 'default',                             #
#         '/users/(.+)/frontpage', 'frontpage',       #
#         '/users/(.+)/history/(.+)', 'history',      #
#         '/articles/(.+)/wtr', 'vote',               #
#         '/articles/(.+)/for/(.+)/wtr', 'vote_term', #
#         '/articles/(.+)/callout', 'callout',        #
#         '/articles/(.+)', 'article',                #
#         '/users/(.+)/search', 'search_results',     #
#         '/users/(.+)/compose', 'compose',           #
#         '/admin/recluster', 'recluster')            #
#######################################################

urls = []

#_texas_ is assigned to the state that we're concerned with.  In honor
#of Christine, 'casue I can't think of a better name
texas = state.the
search = texas.search

class BitBucket:
  def write(self, s): pass

#TODO: this iface makes no sense -- the service will need context, so
#it's silly not to use it to get the username.  Of course, it's also
#impossible to do so.
def user_link(username):
  with link(service=Dummy):
    img(alt='',  src='/static/user.png')
    txt(username)


#### Here's how services work:
# They are subclasses of Service.
#
# They must provide rendering instructions in stream_contents() and
# emit_sidebar().  These methods should display stuff, but they should
# never write to the state.  (Even reading might be a bad idea, but
# I'm doing it for now.)  Actually performing the service happens in
# GET and POST.  (Theoretically, it'd be neat if GET didn't write to
# state at all, but in practice there are sometimes useful things to
# record, even if the operation is mainly a matter of reading.)
#
# The service should also provide a @classmethod to generate a url for
# the service.

class Service:
  web.webapi.internalerror = web.debugerror
  
  def __init__(self):
    import time
    self.start = time.time()

    self.dc = dict()


  def auth(self):
    '''Returns the uid, if the user is logged in.  If the username is
provided (e.g., from a URL), try that one.  Otherwise, check the
cookies for the last session.  

Require a proper login with a password before doing anything
serious/unreversable.'''

    cookies = web.cookies()

    #URL first, then cookie
    name = self.dc.pop('username', cookies['name'])
    if name == None:
      raise CantAuth("No username.  Are cookies enabled?")

    try:
      uid = texas.get_uid_from_name(name)
    except: #TODO: be specific about the exception
      raise CantAuth("Unknown username: '%s'" % name)
    if not cookies.has_key('ticket_for_' + str(uid)):
      raise CantAuth("No ticket.  Are cookies enabled?")
    ticket = cookies['ticket_for_' + str(uid)]
    if not texas.check_ticket(uid, ticket):
      raise CantAuth("Incorrect ticket.")

    self.dc['username'] = name
    self.dc['user'] = texas.get_user(uid)
    self.dc['uid'] = uid

    web.setcookie('name', name, expires=3600*24*90)
    web.setcookie('ticket_for_'+str(uid), ticket, expires=3600*24*90)

  def try_auth(self):
    try:
      self.auth()
    except CantAuth, e:
      return False
    return True

  def logout(self):
    #TODO: refuse, unless use has an actual password to log back in with
    if self.dc.has_key('uid'):
      uid = self.dc['uid']
    else:
      try:
        name = web.cookies()['name']
        uid = texas.get_uid_from_name(name)
      except KeyError, e:
        return #Not logged in at all?
    web.setcookie('name', '', expires=-1)
    web.setcookie('ticket_for_'+str(uid), '', expires=-1)

  def emit(self):
    import time

    ret_val = self.emit_full_page()
    log_dbg('total service time: %f seconds' % (time.time() - self.start))
    return ret_val

  def sidebar_contents(self):
    '''Optional body for the sidebar'''
    pass

  def emit_full_page(self):
    '''Standard page structure with a main stream and a sidebar.'''
    with xhtml_document(dc=self.dc, favicon='read.png', 
                        js_files=['jquery-1.2.6.min.js'], stylesheet='yb.css', 
                        title='End of September') as ret_val:
      with div(css='general'): #not sure why the main sidebar is called this...
        #with center():
        with link(service=Dummy, css='bkg_logo'):
          img(src='/static/eos_tree_color_bkg.png', alt='End of September')
        with div(css='sidebarsection', style='margin-top: -27px'):
          with div(style='text-align: center; padding-bottom: 1px',
                   child_sep=" | "):
            if self.dc.has_key('username'): #these don't make sense without one:
              with link(service=Latest):
                txt("read")
                img(alt='', src='/static/read.png')
              with link(service=Compose):
                txt("write")
                img(alt='', src='/static/write.png')
            with link(service=Dummy):
              txt("best of")
              img(alt='', src='/static/bestof.png')
        self.sidebar_contents()
        with form(service=Dummy,
                  style='padding-right: 7px; padding-left: 7px;'):
          textline(style='width: 100%;', name='search')
          with div(style='float: right;'):
            submit(label='search')
          with checkbox(name='recent', checked=True): txt('recent')
          with checkbox(name='local', checked=True): txt('local')
          div(style='clear: both;')
        with div(style='text-align: center;', child_sep=" | "):
          with link(service=Dummy): txt('about')
          with link(service=Dummy): txt('legal')
      with div(css='stream'): #main content area
        with div(css='navbar'):
          if self.dc.has_key('username'):
            if self.dc['uid'] < 10:  #TODO if user is 'real'
              with link(style='float: right', service=Dummy):
                txt("sign out")
              txt("welcome, "); user_link(self.dc['username'])
            else: #guest user
              with link(style='float: right', service=Dummy):
                txt("create permanent account/sign in")
              txt("welcome, guest user "); user_link(self.dc['username'])
          else:
            with link(style='float: right', service=Dummy):
              txt("create account/sign in")
            txt("welcome!")
              
        self.mainstream()

    return ret_val.emit()

class AJAXService(Service):
  '''A service that can deliver just the needed bits of stuff via
AJAX.  self.mainchunk is for the AJAX service, self.mainstream (and
self.sidebar_contents) are for non-AJAX users.'''
  def emit(self):
    import time

    is_ajax = web.input().get('format', None) == 'inner_xhtml'
    if is_ajax:
      ret_val = self.emit_full_page()
    else:
      with just_dc(dc=self.dc) as ret_val:
        self.mainchunk()

    log_dbg('total service time: %f seconds' % (time.time() - self.start))
    return ret_val

#TODO: figure out a way to get undefined HTTP methods return 404 (or whatever)

#these should be paired with a Service or an AJAXService
class Get:
  def GET(self, *args):
    try:
      self.get_exec(*args)
      return self.emit()
    except UserVisibleException, e:
      return e.GET()

class Post:
  def POST(self, *args):
    try:
      self.post_exec(*args)
      return self.emit()
    except UserVisibleException, e:
      return e.GET()

urls += ['/users/([^/]+)/login', 'Login']

class Login(Get, Service, UserTools):
  def get_exec(self, username): #probably should be POST, when we make it work for real
    self.dc['uid'] = texas.get_uid_from_name(username)
    self.dc['username'] = username
    self.issue_credentials()

    web.seeother('/users/'+username+'/latest')

  def mainstream(self): pass #TODO: this is a hack -- we should prevent rendering

urls += ['/users', 'Users']

class Users(Post, Service, UserTools):
  def post_exec(self):
    inp = web.input() #TODO validate
    self.dc['uid'] = texas.create_user(inp.name, inp.pwd, inp.email)
    self.dc['username'] = inp.name
    self.issue_credentials()

    web.seeother('/users/'+inp.name+'/latest')

  def mainstream(self): pass

urls += ['/users/([^/]+)/history/(\d+)', 'History']

class History(Get, Service, ArticleTools):
  def get_exec(self, username, pos):
    self.dc['username'] = username
    self.auth()
    
    self.dc['pos'] = int(pos) #TODO error check 
    self.posts = texas.get_history(self.dc['uid'], self.dc['pos'])

  @classmethod
  def url(cls, tag):
    return "/users/%s/history/%s" % (tag.get_dc('username'),
                                     tag.get_dc('pos'))
  def navvers(self):
    if self.dc['pos'] > 0:
      with link(style='float: left;', service=OlderHistory):
        entity('larr'); txt("older")
    if self.dc['pos'] == self.dc['user'].latest_batch:
      non_ajax_button(style='float: right', service=Latest,
                      label='gather new articles')
    elif self.dc['pos'] == self.dc['user'].latest_batch-1:
        with link(style='float: right;', service=Latest):
          txt("most recent"); entity('rarr')
    else:
        with link(style='float: right;', service=NewerHistory):
          txt("newer"); entity('rarr')
    div(style='clear: both;')
      
  def mainstream(self):
    for post in self.posts:
      self.emit_post(post)

    self.navvers()
    if len(self.posts) == 0:
      with italic():
        txt("You don't seem to have any history in this range.")

  def sidebar_contents(self):
    with paragraph():
      txt("Good times, eh?")

class OlderHistory(History):
  @classmethod
  def url(cls, tag):
    return "/users/%s/history/%s" % (tag.get_dc('username'),
                                    tag.get_dc('pos')-1)
class NewerHistory(History):
  @classmethod
  def url(cls, tag):
    return "/users/%s/history/%s" % (tag.get_dc('username'),
                                    tag.get_dc('pos')+1)  


urls += ['/users/([^/]+)/latest', 'Latest']

class Latest(History, Post):
  def get_exec(self, username): #retrieve the most recent front page
    self.dc['username'] = username
    self.auth()
    
    pos = self.dc['user'].latest_batch
    self.dc['pos'] = pos
    self.fresh = False
    self.posts = texas.get_history(self.dc['uid'], pos)


  def post_exec(self, username): #gather new articles
    self.dc['username'] = username
    self.auth()

    count = int(web.input().get('articles', 6))
    if not 1 < count <= 25:
      count = 6

    self.posts = online.gather(self.dc['user'], texas)[0:count]

    self.fresh = True

    if len(self.posts) > 0:
      texas.inc_batch(self.dc['user'])

    pos = self.dc['user'].latest_batch+1 #the object reflects an out-of-date batch number
    self.dc['pos'] = pos

    for i, post in enumerate(self.posts):
      texas.add_to_history(self.dc['uid'], post.id, pos, i)

    self.auth()

  def mainstream(self):
    if not self.fresh:
      with div(style='text-align: center;'):
        with italic():
          txt("You've seen these already.  You can ")
          non_ajax_button(service=Latest, label='gather new articles')
    posts = self.posts

    for post in posts:
      self.emit_post(post)
    self.navvers()

    if len(posts) == 0:
      with italic():
        txt("There aren't any articles for you at the moment.")

  @classmethod
  def url(cls, doc):
    return "/users/%s/latest" % doc.get_dc('username')

  def sidebar_contents(self):
    with div(css='sidebarsection'):
      with paragraph():
        txt("Pick articles you find insightful, and you'll get more like them.")
      with paragraph():
        txt("The best articles appeal to many different kinds of users.")
    with div(css='sidebarsection'):
      txt("Articles that you find worth the read are saved for "
          "future reference.  Here are some recent ones:")
      with ul(s_id='recentwtr'):
        for pid in texas.recent_votes(self.dc['uid'], 4):
          post = texas.get_post(pid)
          with li(dc={'pid': post.id}):
            with link(css='listedlink', service=Dummy):
              txt(post.claim)
        with link(service=Dummy, style='text-align: right;'):
          txt("more...")


class UserVisibleException(Exception, Get, Service):
   def __init__(self, msg):
     Service.__init__(self) #Get needs no constructor
     Exception.__init__(self, msg)

   def get_exec(self): pass

   def sidebar_contents(self):
     with italic():
       txt(self.msg)
       
   def mainstream(self):
     pass
       
class CantAuth(UserVisibleException):
  def sidebar_contents(self):
    with italic():
      txt("Unable to log in: " + self.message)

  

class IllegalAction(UserVisibleException):
  def __init__(self, msg):
    self.msg = msg



# #/users/<username>/frontpage
# class frontpage(cookie_session, normal_style):
#   def GET(self, username):
#     i = web.input()
#     if(not i.has_key('fresh')):
#       web.seeother('/users/'+username+'/history/latest')
#       return
    
#     uid = self.uid_from_cookie(username) #TODO: handle error

#     user = texas.get_user(uid)
#     user_cluster = user.cid
#     content = ''

#     if(i.has_key('articles')):
#       article_count = int(i['articles'])
#       if article_count < 1 or article_count > 25:
#         article_count = 6
#     else:
#       article_count = 6
    
#     posts = online.gather(user, texas)[0:article_count]
#     for i, post in enumerate(posts):
#       texas.add_to_history(uid, post.id, user.current_batch, i)
#       content += emit_post(post, uid)

#     if len(posts) == 0:
#       content = '<i>We\'re out of articles for you at the moment.  If you\'re halfway normal, there should be some here for you soon.</i>'
#     else:
#       texas.inc_batch(user) #batches seperate the history into pages



#     sidebar = render.ms_sidebar([texas.get_post(wtr) for wtr in texas.recent_votes(uid, 4)])

#     self.package(sidebar,
#         self.nav_wrap(content, username, user.current_batch, True, True),
#         uid < 10, username, js_files=['citizen.js'])

class Article(Get, Post, Service, ArticleTools):
  def get_exec(self, pid):
    pid = int(pid)
    self.post = texas.get_post(pid, content=True)
    self.try_auth()

  def post_exec(self, pid):
    i = web.input() #Someone's composed an article!
    self.auth()
    texas.fill_out_post(pid, self.dc['uid'], i.claim, i.body)
    self.post = texas.get_post(pid, content=True) #and let's take a look at it
    

  @classmethod
  def url(cls, doc):
    return "/articles/"+str(doc.get_dc('pid'))

  def mainstream(self):
    self.emit_post(self.post, expose=True)

  def sidebar_contents(self):
    txt("Lookit that article!  Ain't it a beaut?")
      

urls += ['/compose', 'Compose']

class Compose(Get, Service):
  def get_exec(self):
    self.auth()
    self.dc['pid'] = texas.create_empty_post(self.dc['uid'])

  @classmethod
  def url(cls, doc):
    return '/compose'

  def mainstream(self):
    with form(service=Article, css='post'):
      with h2():
        with span(css='posttitle'):
          #with span(style='font-weight: normal;'): txt("Claim")
          textline(name='claim')
      textarea(name='body', rows='25', css='postbody',
               style='width: 563px;')
      with div(style='text-align: right;'):
        with js_link(fn=dummy_js): txt("enlarge text box")
        submit(label='save draft'); submit(label='publish')
      
  def sidebar_contents(self):
    with div(css='sidebarsection'):
      with paragraph(): txt("Write something interesting.")
      with paragraph():
        txt("Write about a specific")
        with link(service=Dummy): txt("topic")
        txt(", make sure to ")
        with link(service=Dummy): txt("cite")
        txt(" informative sources, and write for ")
        with link(service=Dummy): txt("all kinds of readers")
        txt(".")
    with div(css='sidebarsection'):
      txt("I bet you're thinking that some markup advice would look great here.")

class cookie_session: pass
class normal_style: pass

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
      texas.add_to_history(uid, result.post.id, user.latest_batch, i)
      content += emit_post(result.post, uid, terms, {"score": result.score})

    #TODO inc. batch
      
    sidebar = render.search_sidebar(inp.local)
    self.package(sidebar, content, uid < 10, username, js_files=['citizen.js'])

urls += ['/articles/([^/]+)/wtr', 'Vote']

class Vote(Post, AJAXService, ArticleTools):
  def post_exec(self, pid):
    i = web.input()
    self.auth()
    post = texas.get_post(pid)
    texas.vote(self.dc['uid'], pid)
    if i.has_key('term'):
      texas.add_term(self.dc['uid'], pid, i['iterm'])
    
    texas.fill_out_post(pid, self.dc['uid'], i.claim, i.body)
    self.post = texas.get_post(pid, content=True) #and let's take a look at it

  @classmethod
  def url(cls, doc):
    return "/articles/"+str(doc.get_dc('pid'))+"/wtr"

  def mainstream(self):
    self.emit_post(self.post, expose=True)

  def mainchunk(self):
    self.vote_tools(self.post, voted_for=True)
    
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

urls += ['/articles/([^/]+)/quote', 'Quote']

class Quote(Post, AJAXService, ArticleTools):
  def post_exec(self, pid):
    i = web.input()
    self.auth()


    texas.add_callout_text(pid, self.dc['uid'], i.text)

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
  app = web.application(urls, globals())
  app.run()
  
if __name__ == "__main__":
  serve()

