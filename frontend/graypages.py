from __future__ import with_statement

import web
from datetime import datetime

from backend import state, search, engine, online

from html import *
import js
import human_friendly
from grayservice import Service, AJAXService, Get, Post, CantAuth

from frontend.log import *

log_dbg("Initializing graypages . . .")

#_texas_ is assigned to the state that we're concerned with.  In honor
#of Christine, 'casue I can't think of a better name
texas = state.the
search = texas.search


def emit_full_page(self):
  '''Standard page structure with a main stream and a sidebar.'''
  with xhtml_document(dc=self.dc, favicon='read.png', 
                      js_files=['jquery-1.3.2.min.js', 'citizen.js'],
                      stylesheet='yb.css', 
                      title='End of September') as ret_val:
    with div(css='general'): #not sure why the main sidebar is called this...
      #with center():
      with link(service=Dummy, css='bkg_logo'):
        img(src='/static/eos_tree_color_bkg.png', alt='End of September')
      with div(css='sidebarsection', style='margin-top: -27px'):
        with div(style='text-align: center; padding-bottom: 1px',
                 child_sep=" | "):
          if self.dc.has_key('username'): #these don't make sense without a user:
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
          submit(label='explore')
        with checkbox(name='recent', checked=True): txt('recent')
        if self.dc.has_key('username'):
          with checkbox(name='local', checked=True): txt('local')
        div(style='clear: both;')
      with div(style='text-align: center;', child_sep=" | "):
        with link(service=Dummy): txt('about')
        with link(service=Dummy): txt('legal')
    with div(css='stream'): #main content area
      with div(css='navbar', child_sep=" | "):
        if self.dc.has_key('username'):
          if self.dc['uid'] < 10:  #TODO if user is 'real'
            with span():
              txt("welcome, "); user_link(self.dc['username'])
            with link(service=Dummy):
              txt("log out")
          else: #guest user
            with span():
              txt("welcome, guest user "); user_link(self.dc['username'])
            with link(service=Dummy): txt("create permanent account")
            with link(service=Dummy): txt("log in")
        else:
          txt("welcome!")
          with link(service=Dummy): txt("create account")
          with link(service=Dummy): txt("log in")

      self.mainstream()

  return ret_val.emit()


Service.emit_full_page = emit_full_page


# These tools are mixins intended for use in Service s

class UserTools:
  def auth(self):
    '''Returns the uid, if the user is logged in.  If the username is
provided (e.g., from a URL), try that one.  Otherwise, check the
cookies for the last session.  

Require a proper login with a password before doing anything
serious/unreversable.'''

    cookies = web.cookies()

    if self.dc.has_key('username'):
      name = self.dc.pop('username') #will be reinstated if we validate
    elif cookies.has_key('name'):
      name = cookies['name']
    else:
      raise CantAuth("No username.  Are cookies enabled?")

    try:
      uid = texas.get_uid_from_name(name)
    except DataError, e: #TODO: be specific about the exception
      raise CantAuth("Unknown username: '%s'" % name)
    if not cookies.has_key('ticket_for_' + str(uid)):
      raise CantAuth("No ticket -- you are not logged in.")
    ticket = cookies['ticket_for_' + str(uid)]
    if not texas.check_ticket(uid, ticket):
      raise CantAuth("Incorrect ticket.")

    self.dc['username'] = name
    self.dc['user'] = texas.get_user(uid)
    self.dc['uid'] = uid

    web.setcookie('name', name, expires=3600*24*90)
    web.setcookie('ticket_for_'+str(uid), ticket, expires=3600*24*90)

  def issue_credentials(self):
    web.setcookie('name', self.dc['username'], expires=3600*24*90)
    ticket = texas.make_ticket(self.dc['uid'])
    web.setcookie('ticket_for_'+str(self.dc['uid']), ticket, expires=3600*24*90)


  def try_auth(self):
    try:
      self.auth()
    except CantAuth, e:
      return False
    return True

  def logout(self):
    #TODO: refuse, unless user has an actual password to log back in with
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



class ArticleTools: #for mixing in with Service
  def emit_vote_tools(self, post, voted_for):
    #vote_tools can occur without a post, so it needs ctxid, too.
    with div(dc={'ctxid': post.id, 'pid': post.id,
                 'status_area': 'article_status'},
             idc='tools', css='tools'):
      if self.dc.has_key('terms'):
        terms = self.dc['terms']
        button(dc={'terms': terms}, service=Vote, replace='tools',
               label='... for "%s"' % self.dc['terms'])

      if voted_for:
        with link(service=Article): txt("permalink")
        entity('mdash')
        txt(human_friendly.render_timedelta(datetime.now()
                                            - post.date_posted))
        txt(" ago by ")
        user_link(texas.get_user(post.uid).name)
        button(service=Dummy, label='Good quote', replace='post')
        txt(" ")
      button(service=Vote, label='Worth the read', replace='tools',
             disabled=voted_for)

      br()
      div(idc='article_status')

      
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
        with span(css='posttitle', idc='claim'):
          #with span(style='font-weight: normal;'): txt("Claim: ")
          txt(post.claim)
#        with js_link(fn=js.hide('content')):
#          img(alt='hide', src='/static/x-icon.png')
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



# A note about dc (doc context):

# It exists in two places: there's a hierarchy of it on the tags,
# added to by adding 'dc={...}' to a tag's arg list.  This is picked
# up by the url() classmethod of other Service s to which we are
# creating buttons or links.  There's also the dc of the current
# Service, which we feed to the root of the document, and is used by
# the service itself sometimes.


        

#TODO: this iface makes no sense -- the service will need context, so
#it's silly not to use it to get the username.  Of course, it's also
#impossible to do so.
def user_link(username):
  with link(service=Dummy):
    img(alt='',  src='/static/user.png')
    txt(username)



#### Service implementations ####
urls = []



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
    self.dc['uid'] = texas.create_user(self.param('name'),
                                       self.param('pwd'),
                                       self.param('email'))
    self.dc['username'] = self.param('name')
    self.issue_credentials()

    web.seeother('/users/%s/latest' % self.dc['username'])

  def mainstream(self): pass

urls += ['/users/([^/]+)/history/(\d+)', 'History']

class History(Get, Service, UserTools, ArticleTools):
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
      with ul(ids='recentwtr'):
        for pid in texas.recent_votes(self.dc['uid'], 4):
          post = texas.get_post(pid)
          with li(dc={'pid': post.id}):
            with link(css='listedlink', service=Dummy):
              txt(post.claim)
        with link(service=Dummy, style='text-align: right;'):
          txt("more...")


class Article(Get, Post, Service, UserTools, ArticleTools):
  def get_exec(self, pid):
    pid = int(pid)
    self.post = texas.get_post(pid, content=True)
    self.try_auth()

    if not self.post.published:
      if not (self.dc.has_key('uid') and self.post.pid == self.dc['uid']):
        raise IllegalAction("A draft post can only be viewed by its author.")
        

  def post_exec(self, pid):
    #Someone's composed an article!
    self.auth()
    texas.fill_out_post(pid, self.dc['uid'],
                        self.param('claim'), self.param('body'))
    self.post = texas.get_post(pid, content=True) #and let's take a look at it
    

  @classmethod
  def url(cls, doc):
    return "/articles/"+str(doc.get_dc('pid'))

  def mainstream(self):
    self.emit_post(self.post, expose=True)

  def sidebar_contents(self):
    if self.post.published:
      txt("Lookit that article!  Ain't it a beaut?")
    else:
      txt("This post is a draft, so it's only visible to you.  You can ")
      with link(service=Compose): txt("edit or publish your drafts.")
      

urls += ['/compose', 'Compose']

class Compose(Get, Service, UserTools):
  def get_exec(self):
    self.auth()

    self.drafts = texas.get_drafts(self.dc['uid'])

    if len(self.drafts) == 0:
      self.drafts = [texas.get_post(
        texas.create_empty_post(self.dc['uid']), content=True)]

    
  @classmethod
  def url(cls, doc):
    return '/compose'

  def mainstream(self):
    for draft in self.drafts:
      with form(service=Article, css='post', idc='draft',
                dc={'ctxid': draft.id, 'pid': draft.id}):
        with h2():
          with span(css='posttitle'):
            #with span(style='font-weight: normal;'): txt("Claim")
            textline(name='claim')
        textarea(name='body', rows='25', css='postbody',
                 style='width: 563px;')
        with div(style='text-align: right;'):
          with js_link(fn=dummy_js): txt("enlarge text box")
          button(service=Dummy, replace='draft', label='save draft')
          submit(label='publish')
      
  def sidebar_contents(self):
    with div(css='sidebarsection'):
      with paragraph(): txt("Write something interesting.")
      with paragraph():
        txt("Choose a specific")
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

urls += []

class Search(Post, Service, UserTools, ArticleTools):
  def post_exec(self):
    terms = inp.search

    self.try_auth()

    self.local = self.maybe_param('local', False)

    if self.local:
      self.results = search.local_search(user.cid, terms, self.param('recent'))
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

urls += [r'/articles/([0-9]+)/wtr', 'Vote']

class Vote(Post, AJAXService, UserTools, ArticleTools):
  def post_exec(self, pid):
    log_tmp('post_exec....')
    i = web.input()
    self.auth()

    pid = int(pid)
    self.post = texas.get_post(pid)
    texas.vote(self.dc['uid'], pid)
    if self.has_param('term'):
      texas.add_term(self.dc['uid'], pid, self.param('term'))

  @classmethod
  def url(cls, doc):
    return "/articles/"+str(doc.get_dc('pid'))+"/wtr"

  @classmethod
  def js(cls, url, doc): #TODO: is there a way to plumb 'tools' nicely?
    ctxid = doc.get_dc('ctxid')
    return ("ajax_replace('tools%d', '%s', '%s', 'POST'," %
      (ctxid, url, doc.get_dc('status_area')+str(ctxid)) +
            "function(){add_recent_wtr(%d)});" % ctxid)

  def mainstream(self):
    log_tmp('mainstream')
    self.emit_post(self.post, expose=True)

  def mainchunk(self):
    self.emit_vote_tools(self.post, voted_for=True)
    
urls += ['/articles/([^/]+)/quote', 'Quote']

class Quote(Post, AJAXService, UserTools, ArticleTools):
  def post_exec(self, pid):
    self.auth()

    texas.add_callout_text(pid, self.dc['uid'], self.param('text'))

  def mainstream(self):
    '''Just a status message here for successful quotings.'''


#TODO give BestOf a history
class BestOf(Get, Service, ArticleTools):
  def get_exec(self):
    self.try_auth() #TODO make everything at least try_auth
    
    self.posts = texas.get_best_of(datetime.replace(hour=0, minute=0,
                                                    second=0, microsecond=0))
  @classmethod
  def url(cls, tag):
    return "/bestof"

  def mainstream(self):
    for post in self.posts:
      self.emit_post(post)

    #self.navvers()

  def sidebar_contents(self):
    with paragraph():
      txt("It's the best!")
  

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
  web.webapi.internalerror = web.debugerror
  
  app = web.application(urls, globals())
  app.run()
  
if __name__ == "__main__":
  serve()

