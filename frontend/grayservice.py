from __future__ import with_statement

import web
import time

from html import *
from log import *

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
  def __init__(self):
    self.start = time.time()

    self.dc = dict()
    self._input = web.input()

  def param(self, key):
    '''Use this to access web.input() to get a good error if the param
is not there.'''
    if self._input.has_key(key):
      return self._input[key]
    raise IllegalAction("Form submitted without required field '%s'.  If our site let you do this, it's probably a bug.")

  def maybe_param(self, key, default):
    return self._input.get(key, default)

  def has_param(self, key):
    return self._input.has_key(key)


  # TODO: the two-phase system in html.py makes this difficult...
  # Perhaps we want to simply guarantee that the parent's _dc_ is done
  # before its children are constructed?
  #@classmethod
  #def service_link_prefix(cls, doc):
  #  '''For example, an icon for links to this service'''
  #  pass

  def emit(self):
    ret_val = self.emit_full_page()
    log_dbg('total service time: %f seconds' % (time.time() - self.start))
    return ret_val

  def sidebar_contents(self):
    '''Optional body for the sidebar'''
    pass


class AJAXService(Service):
  '''A service that can deliver just the needed bits of stuff via
AJAX.  self.mainchunk is for the AJAX service, self.mainstream (and
self.sidebar_contents) are for non-AJAX users.'''
  def emit(self):
    import time

    is_ajax = self.maybe_param('format', None) == 'inner_xhtml'
    if is_ajax:
      with just_dc(dc=self.dc) as ret_val:
        self.mainchunk()
    else:
      ret_val = self.emit_full_page()
      
    log_dbg('total service time: %f seconds' % (time.time() - self.start))
    return ret_val

#TODO: figure out a way to get undefined HTTP methods return 404 (or whatever)

#these should be paired with a Service or an AJAXService
class Get:
  def GET(self, *args):
#    try:
      self.get_exec(*args)
      return self.emit()
#    except UserVisibleException, e:
#      return e.GET()

class Post:
  def POST(self, *args):
#    try:
      self.post_exec(*args)
      return self.emit()
#    except UserVisibleException, e:
#      raise web.webapi.HTTPError(e.status, {}, e.GET())


# UserVisibleException is caught be the service, and displayed to the
# user instead of normal content.  In the future, they should change
# the HTTP response code

class UserVisibleException(web.webapi._NotFound, Service, Get):
   def __init__(self, msg):
     Service.__init__(self) #Get needs no constructor
     self.msg = msg
     web.webapi._NotFound.__init__(self, self.GET())

   def get_exec(self): pass

   def sidebar_contents(self):
     txt("Need help?  Someday we'll have a support system!")
       
   def mainstream(self):
     with italic():
       txt(self.msg)

class CantAuth(UserVisibleException):
  def mainstream(self):
    with italic():
      txt("Unable to log in: " + self.msg)

class IllegalAction(UserVisibleException): pass

  
