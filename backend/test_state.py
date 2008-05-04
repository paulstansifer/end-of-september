#!/usr/bin/env python

# Unit tests for State class and associated methods.

# $Id: test_state.py 97 2008-03-22 15:10:05Z daniel $

import state
import unittest

from datetime import datetime

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.state = state.State('yb_test')
        self.state.connect()
        self.state.clear()

    def test_handle_missing_user(self):
        self.assertEqual(self.state.get_user(20), None)

    def test_handle_missing_post(self):
        self.assertEqual(self.state.get_post(25), None)

    def test_create_user(self):
        uid = self.state.create_user('user', 'mypass',
                                     'asdf@jklsemicolon.com')
        userinfo = self.state.get_user(uid)
        for field, value in [('name', 'user'),
                             ('password', 'mypass'),
                             ('email', 'asdf@jklsemicolon.com')]:
            self.assertEqual(userinfo[field], value)

    def test_uid_from_name(self):
        uid1 = self.state.create_user('user1', '', '')
        uid2 = self.state.create_user('user2', '', '')
        uid3 = self.state.create_user('user3', '', '')
        self.assertEqual(self.state.get_uid_from_name('user2'), uid2)
        self.assertEqual(self.state.get_uid_from_name('user4'), None)

    def test_create_post(self):
        uid = self.state.create_user('user1', '', '')
        pid = self.state.create_post(uid, 'This works', 'Here\'s why.')
        post = self.state.get_post(pid)
        for field, value in [('uid', uid),
                             ('claim', 'This works'),
                             ('content', 'Here\'s why.')]:
            self.assertEqual(post[field], value)

    def test_vote(self):
        uids = [5,3,4,3,5,7,5,2,5]
        pids = [3,7,4,2,6,2,4,2,7]
        for uid, pid in zip(uids, pids):
            self.state.vote(uid, pid)
        self.assert_(len(self.state.votes_by_uid(5)) == 4)
        self.assert_(len(self.state.votes_for_pid(7)) == 2)
        self.assert_((3,7) in self.state.dump_votes())
        self.assert_((7,2) in self.state.dump_votes())
        self.assert_((4,6) not in self.state.dump_votes())

    def test_multiple_votes(self):
        self.state.vote(3, 4)
        self.state.vote(3, 4)
        votes = self.state.votes_for_pid(4)
        self.assert_(len(votes) == 1)

    def test_clear(self):
        uid = self.state.create_user('user', 'mypass',
                                     'asdf@jklsemicolon.com')
        pid = self.state.create_post(uid, 'This works', 'Here\'s why.')
        self.state.vote(uid, pid)
        self.state.clear()
        self.assertEqual(self.state.get_user(5), None)
        self.assertEqual(self.state.get_post(10), None)
        self.assertEqual(self.state.votes_by_uid(5), [])
        self.assertEqual(self.state.votes_for_pid(10), [])

    def test_retired_active(self):
        self.state.setuser(3, 'user', 'mypass',
                           'asdf@jklsemicolon.com',
                           datetime(2008, 1, 2))
        self.assertEqual(self.state.getactive(3), [])
        self.assertEqual(self.state.getretired(3), [])
        self.state.setactive(3, [5, 3, 88])
        self.assertEqual(self.state.getactive(3), [5, 3, 88])
        self.assertEqual(self.state.getretired(3), [])
        self.state.setactive(3, [2, 1])
        self.assertEqual(self.state.getactive(3), [2, 1])
        self.assertEqual(self.state.getretired(3), [5, 3, 88])
        self.state.setactive(3, [42])
        self.assertEqual(self.state.getactive(3), [42])
        self.assertEqual(self.state.getretired(3), [5, 3, 88, 2, 1])
        self.state.undoretire(3, 2)
        self.assertEqual(self.state.getactive(3), [2, 1])
        self.assertEqual(self.state.getretired(3), [5, 3, 88])        

    def test_cluster(self):
        uid = self.state.create_user('user1', '', '')
        self.state.apply_clusters([(uid, 3), (-8, 2)])
        self.assertEqual(self.state.get_user(uid).cid, 3)
        self.assertEqual(self.state.get_users_in_cluster(3)[0], uid)
        self.assertEqual(self.state.get_users_in_cluster(2), [])

if __name__ == '__main__':
    unittest.main()

