from urllib2 import urlopen, HTTPCookieProcessor, build_opener, install_opener
from urllib import urlencode
import HTMLParser, threading
import re
import sys
from log import *

#We can use this for integration tests.  It makes requests and
#screenscrapes the results for results.

base_url = 'http://localhost:8080'

pid_to_epid = {}
epid_to_pid = {}

#screenscraper that returns a list of articles in the response
class _Scraper(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.articles = []

  def handle_starttag(self, tag, attrs):
    if tag == 'div':
      for a,v in attrs:
        if a == 'id':
          match = re.search(r'^post(\d+)$', v)
          if match != None:
            self.articles.append(int(match.group(1)))
                    
install_opener(build_opener(HTTPCookieProcessor()))
            
def _get(addr, base='http://localhost:8080'):
  s = _Scraper()
  url = base + addr
  #log_dbg('[ GET ' + url + ' ]')
  s.feed('\n'.join(urlopen(url).readlines()))
  s.close()
  return s

def _post(addr, data, base='http://localhost:8080'):
  s = _Scraper()
  url = base + addr
  #log_dbg('[ POST ' + url + ' ' + urlencode(data) + ' ]')
  s.feed('\n'.join(urlopen(url, urlencode(data)).readlines()))
  return s

def _become(username):
  #print "becoming", username
  _get('/login?name=' + username)

def get_an_article(username):
  s = _get('/users/' + username + '/frontpage?articles=1')
  if len(s.articles) == 0:
    return -1
  elif len(s.articles) == 1:
    return pid_to_epid[s.articles[0]]
  else:
    raise Exception('More articles returned than requested')

def add_user(username):
  _post('/login', {'name': username, 'pwd': 'asdf1234', 'email': username+'@example.com'})
  #TODO: when user creation is fleshed out, test for success

def vote_for_article(username, epid):
  _become(username)
  s = _post('/articles/'+str(epid_to_pid[epid])+'/wtr')

def compose_article(username, epid):
  _become(username)
  s = _post('/users/'+username+'/compose', {'claim': 'Claim (%s) (%d)' % (username, epid),
                                            'posttext': 'contents'})
  pid = s.articles[0]
  epid_to_pid[epid] = pid
  pid_to_epid[pid] = epid

def dialog():
  import state
  log_dbg('Initializing terminalgray . . .')
  state.the.__init__('yb_test') #horrible hack,
  #but I can't figure out how to get web.py to let me pass a
  #parameter to graypages
  state.the.clear()

  class GP(threading.Thread):
    def run(self):
      import graypages
      graypages.serve()

  GP().start()
    
  while True:
    cmd = raw_input()
    parts = re.split('\W+', cmd)
    if parts[0] == 'UP':
      vote_for_article('tgu_'+parts[1], int(parts[2]))
    elif parts[0] == 'GET':
      print get_an_article('tgu_' + parts[1])
      sys.stdout.flush()
    elif parts[0] == 'JOIN':
      add_user('tgu_'+parts[1])
    elif parts[0] == 'POST':
      compose_article('tgu_'+parts[1], int(parts[2]))
    elif parts[0] == 'INFO':
      uid = uid_map[parts[1]]
      print state.the.get_user(uid)
    elif parts[0] == 'CLEAR':
      state.the.clear()
    elif parts[0] == 'QUIT':
      return

if __name__ == '__main__':
  dialog()
