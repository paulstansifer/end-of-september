import state, search
import online
import re
import sys
from log import *

state = state.the
    


def operate():
    log_dbg("Initializing terminalgray . . .")

    #map from strings of external ids to ints of internal ones
    uid_map = {}
    pid_map = {}
    e_pid_map = {} #other way around

    while True:
        cmd = raw_input()
        parts = re.split('\W+', cmd)
        if parts[0] == "UP":
            uid = uid_map[parts[1]]
            pid = pid_map[parts[2]]

            state.vote(uid, pid)
        elif parts[0] == "GET":
            uid = uid_map[parts[1]]
            user = state.get_user(uid)
            try:
                post = online.gather(user, state)[0]
                state.add_to_history(uid, post.id)
                print e_pid_map[post.id]
                sys.stdout.flush()
            except IndexError:
                print -1
                sys.stdout.flush()
        elif parts[0] == "JOIN":
            e_uid = parts[1]
            state.create_user('tgu_' + e_uid, 'password' + e_uid, e_uid + '@email.com')
            uid_map[e_uid] = state.get_uid_from_name('tgu_' + e_uid)
        elif parts[0] == "POST":
            uid = uid_map[parts[1]]
            e_pid = parts[2]

            pid = state.create_post(uid, "Claim", "Contents (" + cmd + ")")
            e_pid_map[pid] = e_pid
            pid_map[e_pid] = pid
        elif parts[0] == "INFO":
            uid = uid_map[parts[1]]
            print state.get_user(uid)
        elif parts[0] == "CLEAR":
            state.clear()
        elif parts[0] == "QUIT":
            return
        

if __name__ == "__main__":
    state.connect()
    operate()
