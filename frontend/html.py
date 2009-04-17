from log import *
import web

class Dummy:
    def url(self, tag):
        return "/something/"+tag.get_info('id')

    def js_call(self, tag):
        return "javascript:alert('not implemented!')"

dummy = Dummy()

#TODO: one final rewrite (I hope!)  Switch to imperative form, using "with" blocks for structure.

tag_stack = [None]


class txt:
    def __init__(self, t):
        self.t = t
        self.parent = tag_stack[-1]
        if self.parent != None:
            self.parent.children.append(self)
            
    def emit(self):
        return web.net.htmlquote(self.t)
    
class tag:
    def __init__(self, name=None, info=None, **attrs):
        self.name = name
        if attrs.has_key('info'):
            self.info = attrs.pop('info')
        else:
            self.info = info
        
        self.attrs = attrs
        self.children = []

        self.parent = tag_stack[-1] #parent is on top of the stack
        if self.parent != None:
            self.parent.children.append(self)

        #for c in children:
        #    if not isinstance(c, str):
        #        c.parent = self

    def __enter__(self):
        tag_stack.append(self)
        return self

    def __exit__(self, type, value, traceback):
        tag_stack.pop()
        

    def get_info(self, key):
        if self.info != None  and  self.info.has_key(key):
            return self.info[key]
        else:
            return self.parent.get_info(key)
        
    #(new copy, side-effectless) add the given children to this tag
    #def __call__(self, *children):
    #    import copy
    #    ret_val = copy.copy(self)
    #    ret_val.children = children
    #    for c in children:
    #        if not isinstance(c, str):
    #            c.parent = ret_val
    #    return ret_val


    def emit_kids(self):
        accum = ""
        for c in self.children:
            #if isinstance(c, str):
            #    accum += web.net.htmlquote(c)
            #else:
            accum += c.emit()
        return accum

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
                at['id'] = at.pop('c_id')+self.get_info('id')
            
            ret_val = ""
            for k, v in at.items():
                ret_val += " %s='%s'" % (k, v)
            return ret_val

    def __str__(self):
        return self.emit()

    def emit(self):
        return "<%s%s>%s</%s>" % (
            self.name, self.emit_attrs(), self.emit_kids(), self.name)



class root_info(tag):
    def __init__(self, info, *children):
        tag.__init__(self, None, *children)
        self.info = info

    def get_info(self, key):
        return self.info[key]

    def emit(self):
        return self.emit_kids()

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
def _make_default_tag(name):
    return lambda **attrs: tag(name, **attrs)

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


#button
#link
#js_link
#root_info
    
