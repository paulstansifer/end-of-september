from math import sqrt
from random import randint, sample
from datetime import timedelta, datetime
from frontend.log import *

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

def calculate_broad_support(pid, state):
    '''Used by state to keep the cached DB value up-to-date.'''
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

def uniq_posts(list):
    retval = []
    for idx in xrange(len(list)):
        if idx == 0 or list[idx-1].id != list[idx].id:
            retval.append(list[idx])
    return retval

def rate_recent_article(article):
    #article = state.getpost(vote['pid'])
    age_td = datetime.now() - article.date_posted
    age = age_td.days + age_td.seconds / (60 * 60 * 24)
    #broad_support has a theoretical maximum of 1, let's say.
    return article.broad_support - sqrt(age) * 0.1

def cmp_recent_articles(a, b):
    return cmp(rate_recent_article(b), rate_recent_article(a)) 

def gather_global(state):
  delg_ids = []

  for cluster in state.db.query('SELECT * FROM cluster'):
    delg_ids += [d.id for d in
                 state.get_sample_users_in_cluster(cluster.id, 10)]

  return _collect_from_delegates(delg_ids, 5, state)
    

def gather(user, state):
  import time;  start = time.time()
  #log_tmp("ONLINE: cid " + str(user.cid))
  nearby = state.connected_cluster_sample(user.cid, 3)
  #log_tmp("ONLINE: nearby  " + str(nearby))
  
  delg_ids = []

  #get around 20 users.  Hopefully, some will be interesting.
  for c in nearby:
    delg_ids += [d.id for d in
                 state.get_sample_users_in_cluster(c, 20/len(nearby))]

  #log_tmp("ONLINE: delegates " + str(delg_ids))

  return _collect_from_delegates(delg_ids, 4, state, user)
  #log_dbg('gather time: %f seconds' % (time.time() - start))


def _collect_from_delegates(delg_ids, votes_per_delg, state, specific_voter=None):
  #get four recent votes per user
  possible_articles = []
  for delg_id in delg_ids:
    #if users' implicit votes for their own articles are not stored
    #explicitly, we need to factor them in here.  Also, we might want
    #to give the self-votes a little more power at this point, just to
    #get articles started
    if specific_voter != None:
      votes = state.recent_unviewed_votes(delg_id, specific_voter.id,
                                          votes_per_delg)
    else:
      votes = state.recent_unbestof_votes(delg_id, votes_per_delg)
    #log_tmp("ONLINE: new votes " + str(votes))
    possible_articles += [state.get_post(vote, content=True) for vote in votes]
    #log_tmp("ONLINE: possible articles count " + str(len(possible_articles)))

  possible_articles.sort(cmp=cmp_recent_articles)

  return uniq_posts(possible_articles)
