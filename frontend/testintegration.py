import unittest
import time

from frontend.terminalgray import (
  get_articles, add_user, vote_for_article,
  compose_article, get_history)
import frontend.terminalgray


frontend.terminalgray.init()

class TestOperationsFuzzy(unittest.TestCase):
  
  def setUp(self):
    frontend.terminalgray.clear()
    add_user('ruth')
    add_user('ester')
    add_user('job')
    add_user('boaz')
    for x in xrange(0, 20):
      compose_article('job', x)
      compose_article('ester', x+250)
    

  def test_effacity(self):
    #We can't prove that we'll get any more articles than 1, although
    #it's really unlikely that we'll miss our goal by much
    self.assert_(len(get_articles('ruth', 10)) >= 8)
    self.assert_(len(get_articles('ester', 10)) >= 8)
    self.assert_(len(get_articles('job', 10)) >= 8)
    self.assert_(len(get_articles('boaz', 10)) >= 8)

  def test_history(self):
    r_hist = []
    e_hist = []
    j_hist = []
    b_hist = []
    
    r_hist.append(get_articles('ruth', 3))
    e_hist.append(get_articles('ester', 1))
    j_hist = [
      get_articles('job', 1),
      get_articles('job', 2),
      get_articles('job', 6),
      get_articles('job', 40), #graypages limits it to 6, past 25
      get_articles('job', 25),
      get_articles('job', 12)
    ]
    r_hist.append(get_articles('ruth', 0)) #graypages forces it to 6
    e_hist.append(get_articles('ester', 1))
    e_hist.append(get_articles('ester', 2))
    b_hist.append(get_articles('boaz', 25))
    r_hist.append(get_articles('ruth', 6))
    r_hist.append(get_articles('ruth', 7))
    r_hist.append(get_articles('ruth', 8))

    def test(hist, name):
      for i in xrange(0, len(hist)):
        print name, i, hist[i]
        self.assertEqual(hist[i], get_history(name, i+1))
    
    test(r_hist, 'ruth')
    test(e_hist, 'ester')
    test(j_hist, 'job')
    test(b_hist, 'boaz')


    
if __name__ == "__main__":
  #import sys
  #err = sys.stderr
  #sys.stderr = sys.stdout
  unittest.main()
  #sys.stderr = err
