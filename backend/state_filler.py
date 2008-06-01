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

sentences_1 = ['An aardvark, Aaron, abactinally abaft, abandoned an abode.',
               'Abaris articulately ate an abashed abature.',
               'Accredit Abel as an acculturized auditor.']

sentences_2 = ['Babble, barber, but break before Babeldom.',
               'Backbiting bottle-bearers bow between beetles.',
               'Beasts battled back before barbarism.'
               ]

sentences_3 = ['Calvin\'s cabal can\'t carry carcinogins.',
               'Crushed, ceadar chairs cried, "Category contagain!"',
               'Corriander caravels contain certain carryons Ceaser can cover.']

sentences_4 = ['Delicious! Devin\'s dairy-dipped dragonflies don\'t disappoint.',
               'Daggerproof dreadnoughts drag down different destroyers.',
               'Don\'t darken Darrell\'s dreaded demon dairymaids.']

claims = ['P implies Q.',
          'The king of France is bald.',
          'I am the walrus.',
          'If she weighs the same as a duck, she\'s a witch.',
          'Socrates is mortal.',
          'My hovercraft is full of eels.',
          'Colonel Mustard in the conservatory with the candlestick.',
          'Rick Astley will not give you up, let you down, or run around and desert you.',
          'Capital punishment works.  Over 99% of those receiving capital punishment have not returned from the dead.',
          'We should invade all contries of the form /(Ir|C)(a[nqd])+a?/.',
          'Larry Wall and Guido van Rossum should collaborate on a new language project.',
          'We should outlaw tree sap.',
          'I think you\'re pretty sexy, but I hate it when you talk.',
          'The Bible is somewhat fuzzier on the subject of kneecaps.',
          'I\'m not a lion.  You might say that I have a mighty roar, though.',
          ]

sentences_general = [
    'If you\'ll bear with me a moment, this will prove relevant',
    'We\'re revoking your math license.',
    'Alice was the attacker, not Eve!',
    'This crypto system isn\'t a thinly disuigsed Missy Elliot song; it\'s a thinly disguised Dire Straights song!',
    'This can generalize the so-called "friendly numbers" onto the complex plane C.'
    'Let me tell you about my hobby.',
    'That reminds me of a friend of mine, Robert \' DROP TABLE students --.'
    ] + sentences_1 + sentences_2 + sentences_3 + sentences_4 + claims

para = [sentences_1 + sentences_1 + sentences_1 + sentences_general,
        sentences_2 + sentences_2 + sentences_2 + sentences_general,
        sentences_3 + sentences_3 + sentences_3 + sentences_general,
        sentences_4 + sentences_4 + sentences_4 + sentences_general]


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
        topic = randint(0,3)
        file_pid, file_uid = line_parser.match(line).groups()

        if not file_uid in added_file_uids:
            state_uid = state.create_user('_'.join(['user', file_uid]),
                                          passphrase,
                                          ''.join([file_uid, '@gmail.com']))
            uid_file_to_state[file_uid] = state_uid
            added_file_uids.add(file_uid)

        if not file_pid in added_file_pids:
 
            body = ''.join([ '<p>' +
                            ' '.join([sample(para[topic], 1)[0] for k in xrange(randint(1,5))])
                            + '</p>'
                            for j in xrange(randint(1,5))])
            state_pid = state.create_post(1, sample(claims, 1)[0], body)
            pid_file_to_state[file_pid] = state_pid
            added_file_pids.add(file_pid)
        state.vote(uid_file_to_state[file_uid],
                   pid_file_to_state[file_pid],
                   ['a','b','c','d'][topic])
    print "Recalculating scores . . ."
    for post in web.select('post'):
        state.update_support(post.id, online.broad_support_for(post.id, state))
    print "Done."

if __name__ == '__main__':
    s = State()
    s.connect()
    s.clear()
    populate_state(s)
