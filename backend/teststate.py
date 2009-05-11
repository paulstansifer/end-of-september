import state
import unittest
import web

def db_init():
  s = state.State(database='yb_test')
  s.connect()
  s.clear()
  return s

inject = "a'; drop table user; * $ # ! @ ^ & ( ) ` ~ , . --"

class TestState(unittest.TestCase):
  def setUp(self):
    self.s = db_init()
    self.s.clear()
    #TODO: '%' currently causes crashes!
  def tearDown(self):
    self.s.close()

  def run_with_dbg(self, result=None): #rename to _run_ to get live debugging
    if result == None: result = defaultTestCase()
    unittest.TestCase.run(self, result)
    if not result.wasSuccessful():
      print "", result
      print "You can fiddle with the DB from here, or enter 'quit' to finish."
      while True:
        i = raw_input("sql> ")
        if i == "quit": break
        res = web.query(i)
        for r in res: print r
        print len(res), "rows returned"

  def test_c_g_user(self):
    self.assertRaises(Exception, self.s.get_uid_from_name, "DeanVenture")

    for name in [' Brock', 'rus^ty', '', 'HELPeR01234567890123456789012345678901234']:
      self.assertRaises(Exception, self.s.create_user, name, "passwd", "invalid@name.com")
    for name in ['jonas', 'dr.impossible', '-_-']:
      self.s.create_user(name, 'password', name + "@valid.com")
    for pwd in ['a', '%%%%%', '0123456789012345678901234567890012345678901234567890123456789012345']:
      self.assertRaises(Exception, self.s.create_user, 'name', pwd, "invalid@password.com")
    for pwd in ['asfjkl#!@#$^&*()\\;{}[]\'",.<>/?910']:
      self.s.create_user('dr_orpheus', pwd, 'password@valid.com')
    for email in ['asdf.com', '@asdf.com', 'sfd@adsf@asdf.com']:
      self.assertRaises(Exception, self.s.create_user, 'name', 'invalidemail', email)
    for email in ['asdf$asdf+asdf&adsf.adsf...asdf@portable.french.museum']:
      self.s.create_user('dr.henry.killinger', email, 'killinger@example.com')
    
    

    dean_id = self.s.create_user("DeanVenture", "trianna", "dean@venture.com")
    hank_id = self.s.create_user("HankVenture", "the_bat", "hank@venture.com")
    self.assertRaises(Exception, self.s.create_user, "DeanVenture", "trianna", "dean@venture.com")
    

    self.assertEqual(self.s.get_user(dean_id).name, "DeanVenture")
    self.assertEqual(self.s.get_user(hank_id).name, "HankVenture")

    self.assertEqual(self.s.get_uid_from_name("DeanVenture"), dean_id)
    self.assertEqual(self.s.get_uid_from_name("HankVenture"), hank_id)
    self.assertRaises(state.DataError, self.s.get_uid_from_name, "deanVenture")
    self.assertRaises(state.DataError, self.s.get_uid_from_name, "Dean Venture")
    self.assertRaises(state.DataError, self.s.get_uid_from_name, "*")
    self.assertRaises(state.DataError, self.s.get_uid_from_name, inject)    


def seed_state(state):
  ids = {}
  ids['mal'] = state.create_user("malcolm_reynolds", "serenity", "mal@serenity.firefly.org")
  ids['jayne'] = state.create_user("jayne.cobb", "vera", "jayne@serenity.firefly.org")
  ids['wash'] = state.create_user("hobartwashburne", "sudden_inevitable", "wash@serenity.firefly.org")

  ids['violence'] = state.create_post(ids['mal'], "Shooting is the solution to this problem.", "---")
  ids['nonviolence'] = state.create_post(ids['wash'], "Can I make a suggestion that doesn't involve violence?", "---")
  state.vote(ids['jayne'], ids['violence'])
  state.add_term(ids['jayne'], ids['violence'], "violence")
  state.vote(ids['mal'], ids['nonviolence'])

  ids['pants'] = state.create_post(ids['mal'], "Mal needs no pants!", "---")
  return ids
  

class TestStateSeeded(unittest.TestCase):
  def setUp(self):
    self.s = db_init()
    self.ids = seed_state(self.s)

  def tearDown(self):
    self.s.close()

  def test_user_auth(self):
    mal_tik = self.s.make_ticket(self.ids['mal'])
    wash_tik = self.s.make_ticket(self.ids['wash'])

    self.assertEqual(self.s.check_ticket(self.ids['mal'], mal_tik), True)
    self.assertEqual(self.s.check_ticket(self.ids['wash'], wash_tik), True)
    self.assertEqual(self.s.check_ticket(self.ids['mal'], wash_tik), False)
    self.assertEqual(self.s.check_ticket(self.ids['wash'], mal_tik), False)

    self.assertEqual(self.s.check_ticket(self.ids['mal'], "FAKETICKET"), False)
    self.assertEqual(self.s.check_ticket(self.ids['mal'], inject), False)

  def test_vote_analysis(self):
    self.assertEqual(self.s.voted_for(self.ids['mal'], self.ids['violence']), True)
    self.assertEqual(self.s.voted_for(self.ids['jayne'], self.ids['violence']), True)
    self.assertEqual(self.s.voted_for(self.ids['wash'], self.ids['violence']), False)

    self.assertEqual(self.s.voted_for(self.ids['mal'], self.ids['nonviolence']), True)
    self.assertEqual(self.s.voted_for(self.ids['jayne'], self.ids['nonviolence']), False)
    self.assertEqual(self.s.voted_for(self.ids['wash'], self.ids['nonviolence']), True)

    def vbu_ids(name):
      return set([ v.pid for v in self.s.votes_by_uid(self.ids[name])])

    self.assertEqual(vbu_ids('mal'),
                     set([self.ids['violence'], self.ids['nonviolence'], self.ids['pants']]))

    self.assertEqual(vbu_ids('wash'),
                     set([self.ids['nonviolence']]))
  
    #history tested at the integration level

    
if __name__ == "__main__":
  unittest.main()
  

  
