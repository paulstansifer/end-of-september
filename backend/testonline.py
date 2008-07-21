import web
import online
import unittest
import teststate

class TestOnline(unittest.TestCase):
  def setUp(self):
    self.s = teststate.db_init()
    self.ids = teststate.seed_state(self.s)

  def test_broader_support_sanity(self):
    self.assert_(online.broad_support_for(self.ids['violence'], self.s)
                 > online.broad_support_for(self.ids['pants'], self.s))

    self.assert_(online.broad_support_for(self.ids['nonviolence'], self.s)
                 > online.broad_support_for(self.ids['pants'], self.s))

    



if __name__ == "__main__":
  unittest.main()
