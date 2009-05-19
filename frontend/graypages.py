from __future__ import with_statement

from backend import state, search, engine, online

from html import *
from grayservice import Service, AJAXService, Get, Post, CantAuth
import js
import human_friendly
import directory as drct
import graytools as tools

from frontend.log import *

import web
from datetime import datetime, date, timedelta

log_dbg("Initializing graypages . . .")

#_texas_ is assigned to the state that we're concerned with.  In honor
#of Christine, 'casue I can't think of a better name
texas = state.the
search = texas.search

#TODO: it'd be nice to have a @classmethod to generate tags instead of just JS

def emit_full_page(self):
  '''Standard page structure with a main stream and a sidebar.'''
  with xhtml_document(dc=self.dc, favicon='read.png', 
                      js_files=['jquery-1.3.2.min.js', 'citizen.js'],
                      stylesheet='yb.css', 
                      title='End of September') as ret_val:
    with div(css='general'): #not sure why the main sidebar is called this...
      #with center():
      with link(service=drct.Dummy, css='bkg_logo'):
        img(src='/static/eos_tree_color_bkg.png', alt='End of September')
      with div(css='sidebarsection', style='margin-top: -27px'):
        with div(style='text-align: center; padding-bottom: 1px',
                 child_sep=" | "):
          if self.dc.has_key('username'): #these don't make sense without a user:
            with link(service=drct.Latest):
              txt("read")
              img(alt='', src='/static/read.png')
            with link(service=drct.Compose):
              txt("write")
              img(alt='', src='/static/write.png')
          with link(service=drct.Dummy):
            txt("best of")
            img(alt='', src='/static/bestof.png')

      with div(css='sidebarsection', style='text-align: center;', child_sep=" | "):  #previously, css='navbar'
        if self.dc.has_key('username'):
          if self.dc['uid'] < 10:  #TODO if user is 'real'
            with span():
              txt("welcome, "); tools.user_link(self.dc['username'])
            with link(service=drct.Dummy):
              txt("log out")
          else: #guest user
            with span():
              txt("welcome, guest user "); tools.user_link(self.dc['username'])
            with link(service=drct.Dummy): txt("create permanent account")
            with link(service=drct.Dummy): txt("log in")
        else:
          txt("welcome!")
          with link(service=drct.Dummy): txt("create account")
          with link(service=drct.Dummy): txt("log in")

      self.sidebar_contents()
      with form(service=drct.Dummy,
                style='padding-right: 7px; padding-left: 7px;'):
        textline(style='width: 100%;', name='search')
        with div(style='float: right;'):
          submit(label='explore')
        with checkbox(name='recent', checked=True): txt('recent')
        if self.dc.has_key('username'):
          with checkbox(name='local', checked=True): txt('local')
        div(style='clear: both;')
      with div(style='text-align: center;', child_sep=" | "):
        with link(service=drct.Dummy): txt('about')
        with link(service=drct.Dummy): txt('legal')
    with div(css='stream', ids='stream'): #main content area
      div(ids='main_status')
      self.mainstream()

  return ret_val.emit()


Service.emit_full_page = emit_full_page




# A note about dc (doc context):

# It exists in two places: there's a hierarchy of it on the tags,
# added to by adding 'dc={...}' to a tag's arg list.  This is picked
# up by the url() classmethod of other Service s to which we are
# creating buttons or links.  There's also the dc of the current
# Service, which we feed to the root of the document, and is used by
# the service itself sometimes.
    

#### Service implementations ####
class Login(Get, Service, tools.User):
  def get_exec(self, username): #probably should be POST, when we make it work for real
    self.dc['uid'] = texas.get_uid_from_name(username)
    self.dc['username'] = username
    self.issue_credentials()

    web.seeother('/users/'+username+'/latest')

  def mainstream(self): pass #TODO: this is a hack -- we should prevent rendering


class Logout(Get, Service, tools.User):
  def get_exec(self): #is this a GET?  Everyone makes this sort of thing a link
    self.logout()
    web.seeother('/bestof')


class Users(Post, Service, tools.User):
  def post_exec(self):
    inp = web.input()
    self.dc['uid'] = texas.create_user(self.param('name'),
                                       self.param('pwd'),
                                       self.param('email'))
    self.dc['username'] = self.param('name')
    self.issue_credentials()

    web.seeother('/users/%s/latest' % self.dc['username'])

  def mainstream(self): pass


class History(Get, AJAXService, tools.User, tools.Article):
  def get_exec(self, username, pos):
    self.dc['username'] = username
    self.auth()
    
    self.dc['pos'] = int(pos) #TODO error check 
    self.posts = texas.get_history(self.dc['uid'], self.dc['pos'])

  def navvers(self):
    if self.dc['pos'] > 0:
      with link(style='float: left;', service=drct.OlderHistory):
        entity('larr'); txt("older")
    if self.dc['pos'] == self.dc['user'].latest_batch:
      button(style='float: right', service=drct.Latest, 
             label='gather new articles')
    elif self.dc['pos'] == self.dc['user'].latest_batch-1:
        with link(style='float: right;', service=drct.Latest):
          txt("most recent"); entity('rarr')
    else:
        with link(style='float: right;', service=drct.NewerHistory):
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
    count = int(self.maybe_param('articles', 6))
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

  def mainstream(self):
    if not self.fresh:
      with div(style='text-align: center;'):
        with italic():
          txt("You've seen these already.  You can ")
          button(service=drct.Latest, label='gather new articles')
    posts = self.posts

    for post in posts:
      self.emit_post(post)
    self.navvers()

    if len(posts) == 0:
      with italic():
        txt("There aren't any articles for you at the moment.")
        
  def mainchunk(self):
    return self.mainstream() #we're replacing the stream exactly

  def sidebar_contents(self):
    with div(css='sidebarsection'):
      with paragraph():
        txt("Pick articles you find insightful, and you'll get more like them.")
      with paragraph():
        txt("The best articles appeal to many different kinds of users.")
    with div(css='sidebarsection'):
      txt("Articles that you find worth the read are saved for "
          "future reference.  Here are some recent ones:")
      with ul(ids='recentwtr'):
        for pid in texas.recent_votes(self.dc['uid'], 4):
          post = texas.get_post(pid)
          with li(dc={'pid': post.id}):
            with link(css='listedlink', service=drct.Dummy):
              txt(post.claim)
        with link(service=drct.Dummy, style='text-align: right;'):
          txt("more...")


class Article(Get, Post, Service, tools.User, tools.Article):
  def get_exec(self, pid):
    pid = int(pid)
    self.post = texas.get_post(pid, content=True)
    self.try_auth()

    if not self.post.published:
      if not (self.dc.has_key('uid') and self.post.pid == self.dc['uid']):
        raise tools.IllegalAction("A draft post can only be viewed by its author.")
        

  def post_exec(self, pid):
    #Someone's composed an article!
    self.auth()
    texas.fill_out_post(pid, self.dc['uid'],
                        self.param('claim'), self.param('body'))
    self.post = texas.get_post(pid, content=True) #and let's take a look at it

  def mainstream(self):
    self.emit_post(self.post, expose=True)

  def sidebar_contents(self):
    if self.post.published:
      txt("Lookit that article!  Ain't it a beaut?")
    else:
      txt("This post is a draft, so it's only visible to you.  You can ")
      with link(service=drct.Compose): txt("edit or publish your drafts.")
      

class Compose(Get, Service, tools.User):
  def get_exec(self):
    self.auth()

    self.drafts = texas.get_drafts(self.dc['uid'])

    if len(self.drafts) == 0:
      self.drafts = [texas.get_post(
        texas.create_empty_post(self.dc['uid']), content=True)]

  def mainstream(self):
    for draft in self.drafts:
      with form(service=drct.Article, css='post', idc='draft',
                dc={'ctxid': draft.id, 'pid': draft.id}):
        with h2():
          with span(css='posttitle'):
            textline(name='claim')
        textarea(name='body', rows='25', css='postbody',
                 style='width: 563px;')
        with div(style='text-align: right;'):
          with js_link(fn=drct.Dummy): txt("enlarge text box")
          button(service=drct.Dummy, replace='draft', label='save draft')
          submit(label='publish')
      
  def sidebar_contents(self):
    with div(css='sidebarsection'):
      with paragraph(): txt("Write something interesting.")
      with paragraph():
        txt("Choose a specific")
        with link(service=drct.Dummy): txt("topic")
        txt(", make sure to ")
        with link(service=drct.Dummy): txt("cite")
        txt(" informative sources, and write for ")
        with link(service=drct.Dummy): txt("all kinds of readers")
        txt(".")
    with div(css='sidebarsection'):
      txt("I bet you're thinking that some markup advice would look great here.")

class cookie_session: pass
class normal_style: pass

class Search(Post, Service, tools.User, tools.Article):
  def post_exec(self):
    terms = inp.search
    self.try_auth()

    self.local = self.maybe_param('local', False)

    if self.local:
      self.results = search.local_search(self.dc['user'].cid, terms,
                                         self.param('recent'))
    else:
      self.results = search.global_search(terms, self.param('recent'))

    for i, result in enumerate(self.results):
      texas.add_to_history(self.dc['uid'], result.post.id,
                           self.dc['user'].latest_batch, i)

  def mainstream(self):
    for result in self.results:
      self.emit_post(result.post)

  def sidebar(self):
    #TODO: figure out whether we're Bayesian or fulltext fallback
    txt("Search!  It's complicated.")


class Vote(Post, AJAXService, tools.User, tools.Article):
  def post_exec(self, pid):
    log_tmp('post_exec....')
    i = web.input()
    self.auth()

    pid = int(pid)
    self.post = texas.get_post(pid)
    texas.vote(self.dc['uid'], pid)
    if self.has_param('term'):
      texas.add_term(self.dc['uid'], pid, self.param('term'))

  def mainstream(self):
    log_tmp('mainstream')
    self.emit_post(self.post, expose=True)

  def mainchunk(self):
    self.emit_vote_tools(self.post, voted_for=True)
    
class Quote(Post, AJAXService, tools.User, tools.Article):
  def post_exec(self, pid):
    self.auth()
    texas.add_callout_text(pid, self.dc['uid'], self.param('text'))

  def mainstream(self):
    '''Just a status message here for successful quotings.'''

class BestOfHistory(Get, Service, tools.User, tools.Article):
  def get_exec(self, year, month, day):
    self.try_auth() #TODO make everything at least try_auth
    self.dc['date'] = date(int(year), int(month), int(day)) #TODO: deal with errors
    self.posts = texas.get_best_of(self.dc['date'])

  def navvers(self):
    with link(style='float: left;', service=drct.OlderBestOf):
      entity('larr'); txt("older")
    if self.dc['date'] != date.today():
      if self.dc['date'] == date.today() - timedelta(1):
        with link(style='float: right;', service=drct.LatestBestOf):
          txt("today"); entity('rarr')
      else:
        with link(style='float: right;', service=drct.NewerBestOf):
          txt("newer"); entity('rarr')
    div(style='clear: both;')
    
  def mainstream(self):
    for post in self.posts:
      self.emit_post(post)
    self.navvers()

  def sidebar_contents(self):
    with paragraph():
      txt("Four times a day, we gather three of the best articles and put them here.")


class LatestBestOf(BestOfHistory):
  def get_exec(self):
    self.try_auth()    
    self.dc['date'] = date.today()
    self.posts = texas.get_best_of(self.dc['date'])


#TODO: use this to control verbosity, again
def config(wsgifunc):
  bb = BitBucket()
  def ret_val(env, start_resp):
    env['wsgi.errors'] = bb
    return wsgifunc(env, start_resp)
  return ret_val


def serve():
  web.webapi.internalerror = web.debugerror
  web.webapi.db_printing = False
  app = web.application(drct.urls, globals())
  app.run()
  
if __name__ == "__main__":
  serve()
