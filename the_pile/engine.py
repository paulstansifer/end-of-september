#!/usr/bin/python

# Data analysis and recommendation engine for Yeah-But

# $Id: engine.py 61 2008-01-27 16:41:33Z daniel $

from state import State

from random import randint

def cluster_by_votes(state):
    votes = state.dumpvotes()
    uids = set([vote[0] for vote in votes])
    return [(uid, randint(1,3)) for uid in uids]

def recommend_for_cluster(state, cluster):
    users_in_cluster = state.getusersincluster(cluster)
    worthwhile_posts = {}
    for user in users_in_cluster:
        votes = state.votesbyuid(user)
        for vote in votes:
            pid = vote['pid']
            if not pid in worthwhile_posts:
                worthwhile_posts[pid] = 1
            else:
                worthwhile_posts[pid] = worthwhile_posts[pid] + 1
    worthwhile_posts_list = [(worthwhile_posts[k], k) for k in worthwhile_posts]
    worthwhile_posts_list.sort()
    worthwhile_posts_list.reverse()
    return [post[1] for post in worthwhile_posts_list]
