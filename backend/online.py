from math import sqrt
#from state import State
from random import randint, sample
from datetime import timedelta, datetime
import state
import sys #TMP

#The significance of a groups' vote is proportional to the fifth root of its size
fifth_roots = {0: 0, 1: 1, 2: 1.149, 3: 1.246, 5: 1.380, 7: 1.475,
10: 1.585, 15: 1.712, 20: 1.821, 28: 1.947, 38: 2.070, 50: 2.187, 65:
2.305, 85: 2.432, 120: 2.605, 150: 2.724, 200: 2.885, 275: 3.075, 350:
3.227, 450: 3.393, 600: 3.94, 800: 3.807, 1000: 3.981}

frky = fifth_roots.keys()

def fifth_root(val):  #I CAN HAS HAEK?
    l = 0
    u = len(frky)
    while u-l > 1:
        m = int((u + l)/2)
        if frky[m] == val:
            return fifth_roots[frky[m]]
        if frky[m] < val:
            l = m
        else:
            u = m
    return (fifth_roots[frky[l]] + fifth_roots[frky[u]]) / 2

def broad_support_for(pid, state):
    return _broad_support(
        state.get_votes_by_pid_clustered(pid),
        state)

def _broad_support(votes, state):
    retval = 0
    for cluster in xrange(len(votes)):
        vote_count = votes[cluster]
        cluster_size = state.get_cluster_size(cluster)
        if cluster_size == 0:
            continue
        #sys.stderr.write(" (( " + str(vote_count) + "/" + str(cluster_size) + "  --> " + str(sqrt(float(vote_count) / cluster_size)) + ", " +str(fifth_root(cluster_size)) + ")) ")

        retval += sqrt(float(vote_count) / cluster_size) * fifth_root(cluster_size)
    #sys.stderr.write(" [[ " + str(retval) + " ]] \n")
    return retval


#TODO: this is potentially pretty slow, and it can leave us with duplicates
#We could shuffle the lists with each offline update,
#and advance through them, modulo a prime that changes each
#time around.
def pick_reps(list, num):
    if len(list) == 0:
        return []
    return [list[randint(0,len(list)-1)] for x in xrange(1,num)]

def eliminate_consec_dupes(list):
    retval = []
    for idx in xrange(len(list)):
        if idx == 0 or list[idx-1] != list[idx]:
            retval.append(list[idx])
    return retval

def pick_votes(user):
    pass

def rate_recent_article(article):
    #article = state.getpost(vote['pid'])
    age_td = datetime.now() - article.date_posted
    age = age_td.days + age_td.seconds / (60 * 60 * 24)
    #broad_support has a theoretical maximum of 1, let's say.
    return article.broad_support - sqrt(age) * 0.1

def cmp_recent_articles(a, b):
    return  int(rate_recent_article(b)*1000) - int(rate_recent_article(a)*1000) 

def gather(user, state):
    nearby = pick_reps(state.connected_clusters(user.cid), 3)

    delegates = []

    for c in nearby:
        delegates = delegates + pick_reps(state.get_users_in_cluster(c), 4)

    possible_articles = []
    for delg in delegates:
        #if users' implicit votes for their own articles are not stored
        #explicitly, we need to factor them in here.  Also, we might want to give the
        #self-votes a little more power at this point, just to get articles started
        votes = state.recent_votes_by_uid(delg)
        possible_articles += [state.get_post(vote.pid, content=True) for vote in votes]

    possible_articles.sort(cmp=cmp_recent_articles)

    return eliminate_consec_dupes(possible_articles)
