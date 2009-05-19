from backend import state
from html import *
import js
import directory as drct
import human_friendly

from datetime import datetime


texas = state.the

#TODO: this iface makes no sense -- the service will need context, so
#it's silly not to use it to get the username.  Of course, it's also
#impossible to do so.
def user_link(username):
  with link(service=drct.Dummy):
    img(alt='',  src='/static/user.png')
    txt(username)

# These tools are mixins intended for use in Service s

class User:
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
      raise tools.CantAuth("No username.  Are cookies enabled?")

    try:
      uid = texas.get_uid_from_name(name)
    except DataError, e: #TODO: be specific about the exception
      raise tools.CantAuth("Unknown username: '%s'" % name)
    if not cookies.has_key('ticket_for_' + str(uid)):
      raise tools.CantAuth("No ticket -- you are not logged in.")
    ticket = cookies['ticket_for_' + str(uid)]
    if not texas.check_ticket(uid, ticket):
      raise tools.CantAuth("Incorrect ticket.")

    self.dc['username'] = name
    self.dc['user'] = texas.get_user(uid)
    self.dc['uid'] = uid

    web.setcookie('name', name, expires=3600*24*90)
    web.setcookie('ticket_for_'+str(uid), ticket, expires=3600*24*90)

  def issue_credentials(self):
    web.setcookie('name', self.dc['username'], expires=3600*24*90)
    ticket = texas.make_ticket(self.dc['uid'])
    web.setcookie('ticket_for_'+str(self.dc['uid']), ticket,
                  expires=3600*24*90)
    
  def try_auth(self):
    try:
      self.auth()
    except tools.CantAuth, e:
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
    texas.nuke_ticket(self.dc['uid'], web.cookies(ticket_name)) #TODO: handle errors
    web.setcookie('name', '', expires=-1)
    web.setcookie('ticket_for_'+str(uid), '', expires=-1)



class Article: #for mixing in with Service
  def emit_vote_tools(self, post, voted_for):
    #vote_tools can occur without a post, so it needs ctxid, too.
    with div(dc={'ctxid': post.id, 'pid': post.id,
                 'status_area': 'article_status'},
             idc='tools', css='tools'):
      if self.dc.has_key('terms'):
        terms = self.dc['terms']
        button(dc={'terms': terms}, service=drct.Vote, replace='tools',
               label='... for "%s"' % self.dc['terms'])

      if voted_for:
        with link(service=drct.Article): txt("permalink")
        entity('mdash')
        txt(human_friendly.render_timedelta(datetime.now()
                                            - post.date_posted))
        txt(" ago by ")
        user_link(texas.get_user(post.uid).name)
        button(service=drct.Dummy, label='Good quote', replace='post')
        txt(" ")
      button(service=drct.Vote, label='Worth the read', replace='tools',
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
      with js_link(fn=drct.Dummy, css='dismisser'):
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
#             with js_link(fn=drct.Dummy): txt("expand")
#             with link(service=drct.Dummy): txt("page")
#           with div(idc='sidebar_content', css='j_content', expose=expose,
#                    child_sep=" | "):
#             with js_link(fn=drct.Dummy): txt("contract")
#             with link(service=drct.Dummy): txt("page")
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



