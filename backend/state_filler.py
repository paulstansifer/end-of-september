#!/usr/bin/env python

# Quick and dirty data importer of fake data into State.

# $Id: state_filler.py 100 2008-04-11 00:34:48Z paul $

from datetime import datetime
from random import randint, sample
import re
import web

from state import State
import online

paragraphs = ['''Lorem ipsum dolor sit amet, consectetuer adipiscing elit.  Curabitur scelerisque lectus. [/Fusce tempor/], mi a adipiscing tempus, lacus augue luctus sapien, ut commodo arcu tortor cursus leo. Nunc tortor ligula, accumsan non, volutpat in, tristique vel, est. Maecenas aliquam tortor ac purus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.''',
              '''Maecenas ultrices risus ac nunc. Maecenas nonummy. Nunc elit libero, porta et, commodo ut, mollis eu, diam. Maecenas purus tellus, dapibus sed, egestas in, laoreet et, diam. Vestibulum quis leo. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Duis tincidunt.''']
claims = ['P implies Q',
          'The king of France is bald.',
          'I am the walrus.',
          'If she weighs the same as a duck, she\'s a witch.',
          'Socrates is mortal.',
          'My hovercraft is full of eels.',
          'Colonel Mustard in the conservatory with the candlestick.',
          'A vote for Ron Paul is a vote for voting.',
          'Capital punishment works.  Over 99% of those receiving capital punishment have not returned from the dead.',
          'We should invade all contries of the form /(Ir|C)(a[nqd])+a?/.',
          'Larry Wall and Guido van Rossum should collaborate on a new language project.',
          'We should outlaw tree sap.',
          'I think you\'re pretty sexy, but I hate it when you talk.',
          'The Bible is somewhat fuzzier on the subject of kneecaps.',
          'I\'m not a lion.  You might say that I have a mighty roar, though.'
          ]
passphrase = 'Some people have passphrases.  Bruce Schneier has an epic passpoem recounting the story of the three great cryptographers behind RSA.'

def populate_state(state):
    print "Clearing state . . ."
    state.clear()

    added_file_uids = set()
    added_file_pids = set()

    uid_file_to_state = {}
    pid_file_to_state = {}

    line_parser = re.compile(r'(.*)\|(.*)')

    print "Reading 'model_output.dat' . . ."
    for line in file('model_output.dat').readlines():
        file_pid, file_uid = line_parser.match(line).groups()

        if not file_uid in added_file_uids:
            state_uid = state.create_user('_'.join(['user', file_uid]),
                                          passphrase,
                                          ''.join([file_uid, '@gmail.com']))
            uid_file_to_state[file_uid] = state_uid
            added_file_uids.add(file_uid)

        if not file_pid in added_file_pids:
            body = ''.join([ '<p>' + paragraphs[randint(0,1)] + '</p>'
                            for j in xrange(randint(1,4))])
            state_pid = state.create_post(1, sample(claims, 1)[0], body)
            pid_file_to_state[file_pid] = state_pid
            added_file_pids.add(file_pid)
        state.vote(uid_file_to_state[file_uid],
                   pid_file_to_state[file_pid])
    print "Recalculating scores . . ."
    for post in web.select('post'):
        state.update_support(post.id, online.broad_support_for(post.id, state))
    print "Done."

if __name__ == '__main__':
    s = State()
    s.connect()
    s.clear()
    populate_state(s)
