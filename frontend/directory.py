class Dummy:
  @classmethod
  def url(cls, tag):
    return "/something/" #+tag.get_dc('id')

  @classmethod
  def js(cls, doc, tag):
    return "alert('not implemented!')"

  @classmethod
  def client_js(cls, tag):
    return "alert('not implemented!')"


# Trickery warning: the service names in the url/service pairs refer
# to classes in graypages, not here!  Therefore, the names must
# correspond.

urls = []
urls += ['/users/([^/]+)/login', 'Login'] #(username)
class Login:
  @classmethod
  def url(cls, tag):
    return


urls += ['/users/([^/]+)/logout', 'Logout']
  
urls += ['/users', 'Users']

urls += ['/users/([^/]+)/history/(\d+)', 'History']
class History:
  @classmethod
  def url(cls, tag):
    return "/users/%s/history/%s" % (tag.get_dc('username'),
                                     tag.get_dc('pos'))
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
class Latest:
  @classmethod
  def url(cls, doc):
    return "/users/%s/latest" % doc.get_dc('username')

  @classmethod
  def js(cls, url, doc): #TODO: 'main_status' could be defined in a better place
    return ("ajax_replace('stream', '%s', 'main_status', 'POST', null)" % url)


urls += ['/articles/([0-9]+)', 'Article']
class Article:
  @classmethod
  def url(cls, doc):
    return "/articles/"+str(doc.get_dc('pid'))


urls += ['/compose', 'Compose']
class Compose:
  @classmethod
  def url(cls, doc): return '/compose'


urls += ['/search', 'Search']
class Search:
  @classmethod
  def url(cls, doc): return '/search'

urls += ['/articles/([0-9]+)/wtr', 'Vote']
class Vote:
  @classmethod
  def url(cls, doc):
    return "/articles/"+str(doc.get_dc('pid'))+"/wtr"
  
  @classmethod
  def js(cls, url, doc): #TODO: is there a way to plumb 'tools' nicely?
    ctxid = doc.get_dc('ctxid')
    return ("ajax_replace('tools%d', '%s', '%s', 'POST'," %
      (ctxid, url, doc.get_dc('status_area')+str(ctxid)) +
            "function(){add_recent_wtr(%d)});" % ctxid)

urls += ['/articles/([0-9]+)/quote', 'Quote']


urls += ['/bestof/([0-9]{4})-([0-9]{2})-([0-9]{2})', 'BestOfHistory']
class BestOfHistory:
  @classmethod
  def url(cls, tag):
    return "/bestof/" + tag.get_dc('date').isoformat()


urls += ['/bestof', 'LatestBestOf']
class LatestBestOf:
  @classmethod
  def url(cls, tag):
    return "/bestof"

class NewerBestOf(BestOfHistory):
  @classmethod
  def url(cls, tag):
    return "/bestof/" + (tag.get_dc('date') + timedelta(1)).isoformat()

class OlderBestOf(BestOfHistory):
  @classmethod
  def url(cls, tag):
    return "/bestof/" + (tag.get_dc('date') - timedelta(1)).isoformat()
