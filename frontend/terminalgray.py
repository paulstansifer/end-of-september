import state, search
import online
import re

state = state.the
    


def operate():
    print "Initializing terminalgray . . ."

    #map from strings of external ids to ints of internal ones
    uid_map = {}
    pid_map = {}
    e_pid_map = {} #other way around

    while True:
        cmd = raw_input("tg> ")
        parts = re.split('\W+', cmd)
        if parts[0] == "UP":
            uid = uid_map[parts[1]]
            pid = pid_map[parts[2]]

            state.vote(uid, pid)
        elif parts[0] == "GET":
            uid = uid_map[parts[1]]
            user = state.get_user(uid)
            post = online.gather(user, state)[0]
            state.add_to_history(uid, post.id)
            print post.id
        elif parts[0] == "JOIN":
            e_uid = parts[1]
            state.create_user('tgu_' + e_uid, 'password' + e_uid, e_uid + '@email.com')
            uid_map[e_uid] = state.get_uid_from_name('tgu_' + e_uid)
        elif parts[0] == "POST":
            uid = uid_map[parts[1]]
            e_pid = parts[1]

            pid = state.create_post(uid, "Claim", "Contents (" + cmd + ")")
        elif parts[0] == "CLEAR":
            state.clear()
        elif parts[0] == "QUIT":
            return
        

if __name__ == "__main__":
    state.connect()
    operate()
