import web
import online
import unittest
import teststate

class TestOnline(unittest.TestCase):
  def setUp(self):
    self.s = teststate.db_init()
    self.ids = teststate.seed_state(self.s)

  def test_broader_support_sanity(self):
    self.assert_(online.calculate_broad_support(self.ids['violence'], self.s)
                 > online.calculate_broad_support(self.ids['pants'], self.s))

    self.assert_(online.calculate_broad_support(self.ids['nonviolence'], self.s)
                 > online.calculate_broad_support(self.ids['pants'], self.s))
    



if __name__ == "__main__":
  unittest.main()
