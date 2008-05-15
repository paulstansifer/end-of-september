#!/usr/bin/python

# Class and associated files for representing the state of a
# Yeah-But.

# Persistent information will be stored in the databes although this class
# will facilitate caching requests.

# $Id: state.py 100 2008-04-11 00:34:48Z paul $

from datetime import datetime
import web # Needed for database access
import sys
import random # Needed for random cluster assignment hack.  Should disappear

#import search 

class State:
    def __init__(self, database='yb'):
        print >> sys.stderr, 'Initializing State . . .' 

        self.database = database
        random.seed()

        # as MySQL root: GRANT ALL ON yb.* to 'yeahbut'@'localhost';
        web.config.db_parameters = dict(
            dbn='mysql',
            user='yeahbut',
            host='localhost',
            pw='',
            db=self.database)

        self.cluster_size_cache = {}

    # For use when web server is NOT running
    def connect(self):
        web.connect(dbn='mysql',
                    user='yeahbut',
                    host='localhost',
                    pw='',
                    db=self.database)

    def clear(self):
        for table in ['user', 'ticket', 'post', 'vote', 'cluster']:
            web.delete(table, where='1=1')


    def create_user(self, name, pwd, email):
        users_with_name = web.select('user',
                                     where = 'name=%s' % web.sqlquote(name))
        if len(users_with_name) is not 0: return None
        new_user = int(web.insert('user', name=name, password=pwd, email=email))
        self._setcluster(new_user, random.randint(0,4)) #TODO temporary hack
        return new_user

    def check_ticket(self, uid, ticket):
        if len(web.select('ticket', where='uid=%d and ticket=%s' % (uid, web.sqlquote(ticket)))) == 0:
            return False
        else:
            web.update('ticket', where='uid=%d and ticket=%s' %
                       (uid, web.sqlquote(ticket)),
                       last_used=datetime.now().isoformat())
            return True

    def make_ticket(self, uid):
        ticket = str(random.randint(0, 2**128))
        web.insert('ticket', uid=uid, ticket=ticket,
                   last_used=datetime.now().isoformat())
        return ticket
    
    def get_user(self, uid):
        user = web.select('user', where = 'id=%s' % web.sqlquote(uid))
        if len(user) is 0: return None
        return user[0]

    def get_uid_from_name(self, name):
        user = web.select('user', where='name=%s' % web.sqlquote(name))
        if len(user) is 0: return None
        return int(user[0].id)

    
    def create_post(self, uid, claim, content):
        new_post = int(web.insert('post', uid=uid,
                                  claim=claim,
                                  broad_support=-1))#TMP -- should probably leave out
        web.insert('post_content', pid=new_post, raw=content, tokens = 'TODO', safe_html='TODO')
        
        self.vote(uid, new_post)
        #search.
        return new_post

    def get_post(self, pid, content=False):
        if content == False:
            post = web.select('post', where='id=%d' % pid)

        if len(post) is 0: return None
        #else:
        #    post = web.query('select id,uid,claim,broad_support,date_posted,%s from post inner join on post.id = post_content.pid where id=%d', web.sqlquote(content), pid)
        lazies = {
            'raw' : (lambda : web.query('select raw from post_content where pid=%d' % pid)[0].raw),
            'safe_html' : (lambda : web.query('select safe_html from post_content where pid=%d' % pid)[0].safe_html),
            'tokens' : (lambda : web.query('select tokens from post_content where pid=%d' % pid)[0].tokens)
            }
        lazies.update(post[0])
        
        return web.storage(lazies)

    def get_random_posts(self, count):
        return web.select('post', order='rand', limit='%d' % count)

    def vote(self, uid, pid):
        #let's avoid return values unless we know we need them

        #previous_vote = web.select('vote',
        #                           where = 'uid=%d and pid=%d' % (uid, pid))
        #if len(previous_vote) is not 0:
        #    vote = previous_vote[0]
        #else:
        #    vote = int(web.insert('vote', uid=uid, pid=pid))
        #return vote
        if len(web.select('vote', where='uid=%d and pid=%d' % (uid, pid))) == 0:
            web.insert('vote', uid=uid, pid=pid)

        # otherwise vote already exists -- do nothing

    def voted_for(self, uid, pid):
        return len(web.select('vote', where='uid=%d and pid=%d' % (uid, pid))) > 0

    def update_support(self, pid, support):
        web.update('post', where='id=%d' % pid, broad_support=support)

    def dump_votes(self):
        votes = web.select('vote')
        return [(vote.uid, vote.pid) for vote in votes]

    def votes_by_uid(self, uid):
        votes = web.select('vote', where = 'uid=%d' % uid)
        if len(votes) is 0: return []
        return votes

    def recent_votes_by_uid(self, uid):
        #TODO: add a limit parameter and respect it.
        return self.votes_by_uid(uid)

    def votes_for_pid(self, pid):
        votes = web.select('vote', where = 'pid=%d' % pid) 
        if len(votes) is 0: return []
        return votes


    def get_num_clusters(self):
        num_query = web.select('vote', what='count(*)')
        num_clusters = num_query[0]['count(*)']
        return num_clusters

    def get_users_in_cluster(self, cluster):
        users = web.select('user', where='cid=%s' % web.sqlquote(cluster))
        return [u.id for u in users]
        
    def _setcluster(self, uid, new_cluster):
        uid_user = self.get_user(uid)
        if uid_user is None: return
        old_cluster = uid_user.cid
        web.update('user', where='id=%d' % uid,
                   cid=new_cluster)

    def apply_clusters(self, assignments):
        for uid, cluster in assignments:
            self._setcluster(uid, cluster)

    def get_cluster_by_uid(self, uid):
        return self.get_user(uid).cluster

    def get_cluster_size(self, cluster):
        #maybe setdefault is better, but I couldn't get it to work.  PS
        if self.cluster_size_cache.has_key(cluster):
            return self.cluster_size_cache[cluster]
        else:
            rec = int(web.select('user', what='count(*)',
                          where='cid=%d' % cluster)[0]['count(*)'])
            self.cluster_size_cache[cluster] = rec
            return rec

    def get_votes_by_pid_clustered(self, pid):
        self.cluster_count = 5 #TODO update with each rebasing, not here

        vote_list = web.query('''
        select user.cid, count(*) from vote
        inner join user on vote.uid=user.id
        where pid=%d
        group by user.cid
        ''' % pid)
        retval = [0 for c in xrange(self.cluster_count)]
        for record in vote_list:
            retval[record['cid']] = record['count(*)']
        return retval

    def get_term_popularity(self, term):
        return web.query('select count(*) from relevance where term=%s' % sqlquote(term))['count(*)']

    def get_term_in_clusters(self, term, clusters):
        return [r.pid for r in web.select('relevance', where='term=' + web.sqlquote(term) + ' and cid in (' + sqllist(clusters) + ')')]

    # TODO: fix below

    def getactive(self, uid):
        if uid not in self.active: return None
        return self.active[uid]

    def setactive(self, uid, pid_list):
        if uid not in self.active: return
        if uid not in self.retired: return
        self.retired[uid].extend(self.active[uid])
        self.active[uid] = pid_list

    def getretired(self, uid):
        if uid not in self.retired: return None
        return self.retired[uid]

    def undoretire(self, uid, num_articles):
        if uid not in self.active: return
        if uid not in self.retired: return
        self.active[uid] = self.retired[uid][-num_articles:]
        self.retired[uid] = self.retired[uid][:-num_articles]

    #clusters are in a graph, defined by _connections_
#    def _process_connection_list(self, graph):
#        for pair in graph:
#            self._add_connection(pair[0], pair[1])
#    
#    def _add_connection(self, clust1, clust2):
#        self.connections[clust1].append(clust2)
#        self.connections[clust2].append(clust1)
#        
    def connected_clusters(self, cluster):
        return xrange(4) #temporary -- all clusters are connected
#        return self.connections[clust]
