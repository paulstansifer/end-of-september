from log import *
import web

class Dummy:
  @classmethod
  def url(self, tag):
    return "/something/" #+tag.get_dc('id')

  @classmethod
  def js_call(self, tag):
    return "javascript:alert('not implemented!')"

tag_stack = [None]


class txt:
  def __init__(self, t):
    self.t = t
    self.parent = tag_stack[-1]
    if self.parent != None:
      self.parent.children.append(self)
            
  def emit(self):
    return web.net.htmlquote(self.t)

# _dc_ means "document context".  It's information that gets inherited
# along the document structure.

class tag:
  def __init__(self, tagname=None, **attrs):
    self.tagname = tagname

    self.dc = attrs.pop('dc', None)
        
    self.attrs = attrs
    self.children = []

    self.parent = tag_stack[-1] #parent is on top of the stack
    if self.parent != None:
      self.parent.children.append(self)

  def __enter__(self):
    tag_stack.append(self)
    return self

  def __exit__(self, type, value, traceback):
    tag_stack.pop()
        

  def get_dc(self, key):
    if self.dc != None  and  self.dc.has_key(key):
      return self.dc[key]
    else:
      return self.parent.get_dc(key)

  def __repr__(self):
    return "[tag: <%s %s>]" % (self.tagname, self.attrs)

  #TODO: make it omit prefix and suffix if there are no children,
  # and possibly consider empty children to be absent.  Also,
  # consider allowing tags, not just text.  (problem: then text
  # would be inconsistent between txt() in blocks and being bare in
  # parameters)
  def emit_kids(self):
    prefix = self.attrs.pop('prefix', '')
    sep = self.attrs.pop('child_sep', '')
    suffix = self.attrs.pop('suffix', '')
    return prefix + sep.join(c.emit() for c in self.children) + suffix

  def _add_css(self, css):
    if self.attrs.has_key('css'):
      self.attrs['css'] += ' ' + css
    else:
      self.attrs['css'] = css

  def emit_attrs(self):
    if len(self.attrs) == 0:
      return ''
    else:
      at = self.attrs
    if at.get('expose', False):
      self._add_css('exposed')

    if at.has_key('css'):
      at['class'] = at.pop('css')
    if at.has_key('c_id'):
      at['id'] = at.pop('c_id')+self.get_dc('id')
            
    ret_val = ""
    for k, v in at.items():
      ret_val += " %s='%s'" % (k, v)
    return ret_val

  def __str__(self):
    return self.emit()

  def emit(self):
    return "<%s%s>%s</%s>" % (
      self.tagname, self.emit_attrs(), self.emit_kids(), self.tagname)

class main_document(tag):
  def get_dc(self, key): #end of the line
      return self.dc[key]

  def emit(self):
    scripts = self.attrs.pop('js_files')
    stylesheet = self.attrs.pop('stylesheet')
    favicon = self.attrs.pop('favicon')
    title = self.attrs.pop('title')
    
    return ('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html><head><title>%s</title>
<link rel="stylesheet" type="text/css" href="/static/%s" />
<link rel="shortcut icon" href="/static/%s" />''' % (title, stylesheet, favicon)
+ ''.join('<script src="/static/%s" type="text/javascript"></script>' % 
          script for script in scripts)
+ '</head><body>' + self.emit_kids() + '</body></html>')

class button(tag):
  def emit(self):
    url = self.attrs.pop('service').url(self) #have the service figure out its URL
    label = self.attrs.pop('label')
    replace = self.attrs.pop('replace')
    uniq_id = url.replace('/','_')
    return """<form action='%s' method='post' style='display:inline;'>
<input type='button' value='%s'
onclick='javascript:ajax_replace("%s", "%s", "status_%s", "POST")'%s/>
</form>""" % (url, label, replace, url, uniq_id, self.emit_attrs())#, uniq_id)

class non_ajax_button(tag):
  def emit(self):
    url = self.attrs.pop('service').url(self)
    label = self.attrs.pop('label')
    return """<form action='%s' method='post' style='display:inline;'>
<input type='button' value='%s'%s/></form>""" % (url, label, self.emit_attrs())

    
class link(tag):
  def emit(self):
    url = self.attrs.pop('service').url(self)
    return "<a href='%s'%s>%s</a>" % (url, self.emit_attrs(), self.emit_kids())

#TODO: pretty up the function call interface.

#Maybe add some decoration...
class js_link(tag):
  def emit(self):
    self._add_css('js_link') #hidden by default, js exposes?
    js_call = self.attrs.pop('fn').js_call(self)
    #before = self.attrs.pop('before', '')
    #after = self.attrs.pop('after', '')
    return "<a href='javascript:%s'%s>%s</a>" % (
        web.net.htmlquote(js_call), self.emit_attrs(), self.emit_kids())

class form(tag):
  def emit(self):
    url = self.attrs.pop('service').url(self)
    return "<form action='%s'%s>%s</form>" % (
      url, self.emit_attrs(), self.emit_kids())

class textline(tag):
  def emit(self):
    self.attrs['type'] = 'text'
    return "<input%s />" % self.emit_attrs()

class checkbox(tag):
  def emit(self):
    self.attrs['type'] = 'checkbox'
    uniq_id = self.attrs['name'] #we also need 'name' as an attr
    self.attrs['id'] = uniq_id

    if self.attrs.pop('checked', False):
      self.attrs['checked'] = 'checked'
    return ("<input%s /><label for='%s'>" % (self.emit_attrs(), uniq_id) 
            + self.emit_kids() + "</label>")
    
class submit(tag):
  def emit(self):
    self.attrs['type'] = 'submit'
    self.attrs['value'] = self.attrs.pop('label')
    return "<input%s />" % self.emit_attrs()
    
def _make_default_tag(tagname):
  return lambda **attrs: tag(tagname, **attrs)

h1 = _make_default_tag('h1')
h2 = _make_default_tag('h2')
h3 = _make_default_tag('h3')
h4 = _make_default_tag('h4')
div = _make_default_tag('div')
ul = _make_default_tag('ul')
ol = _make_default_tag('ol')
li = _make_default_tag('li')
span = _make_default_tag('span')
img = _make_default_tag('img')
bold = _make_default_tag('b')
italic = _make_default_tag('i')
em = _make_default_tag('em')
br = _make_default_tag('br')
paragraph = _make_default_tag('p')

#button
#link
#js_link
    
