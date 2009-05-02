#!/usr/bin/python

# Class and associated files for representing the state of a
# Yeah-But.

# Persistent information will be stored in the databes although this class
# will facilitate caching requests.

# $Id: state.py 100 2008-04-11 00:34:48Z paul $

from datetime import datetime
import re
import random # Needed for random cluster assignment hack.  Should disappear

import web # Needed for database access

from frontend.log import *
import search

class DataError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def sql_str(s):
  return "'" + (s.replace("\\", "\\\\").replace("'", "\\'")
                 .replace("\0", "\\\0")) + "'"


_name_validator = re.compile(r'^[\w.-]{1,32}$')
def _validate_name(name):
  if not _name_validator.match(name):
    raise DataError("Invalid username: '%s'.  Usernames must be no more than 32 characters, and consist solely of alphanumerics, underscore, period, and dash" % name)

_email_validator = re.compile(r'[^@]+@[a-z-]+([.][a-z-]+)+', re.I)
def _validate_email_address(email):
  if len(email) > 64: raise DataError("Invalid email address: '%s'.  We can only store 64 characters of email address.")
  if not _email_validator.match(email):
    raise DataError("Invalid email address: '%s'.  We won't be able to figure out how to send mail to that address.")
#TODO: check for common mistakes that might not be mistakes in Javascript
#_probable_email_address = re.compile(r'[\w.+-]+@[a-z-]+([.][a-z-]+)*[.][a-z]{2,4}', 'I')
_pwd_validator = re.compile(r'^[^%]{4,64}$')  #TODO: permit '%'s when web.py can deal with it
def _validate_password(pwd):
  if not _pwd_validator.match(pwd):
    raise DataError("Invalid password.  Passwords must be between 4 and 64 characters, and not contain the character '%'")


#TODO: catch MySQL exceptions and raise custom ones.
  
class State:
    def __init__(self, database='yb'):
        log_dbg('Initializing state (%s) . . .' % database)
        
        random.seed()

        # as MySQL root: GRANT ALL ON yb.* to 'yeahbut'@'localhost';
        self.db = web.database(
          dbn='mysql',
          user='yeahbut',
          pw='',
          db=database,
          charset='utf8')
        

        #self.ssh_client = paramiko.SSHClient()
        self.cluster_size_cache = {}

        self.search = search.Search(database)

        try:
          self.active_cid = self.db.query('select active_cid from globals')[0].active_cid;
        except IndexError:
          self.active_cid = None #presumably, the first thing we'll do is clear the DB

    #mainly for testing, when we need to repeatedly make sane states
    def close(self):
      self.search.close()

      
    # For use when web server is NOT running
    def connect(self, database='yb'):
        #self.db.load() #already done above
        pass

    def clear(self): #nuke everything in the database
        for table in ['user', 'ticket', 'post', 'post_content', 'vote',
                      'cluster', 'cluster_connection', 'relevance',
                      'quote', 'history', 'globals']:
            self.db.query('truncate %s' % table)

        self.db.query('insert into globals values (active_cid=0)')
        self.active_cid = 0

        #temporary hack -- all clusters are connected
        for a in xrange(0,5):
            for b in xrange(0,5):
                self.db.query('insert into cluster_connection values (%d, %d)' % (a,b))

        self.search.clear()


    #TODO: impose restrictions on name contents 
    #TODO: don't store password directly!
    #NOTE: MySQL is case-insensitive by default.  Currently, we follow this convention in names.
    def create_user(self, name, pwd, email):
      _validate_name(name)
      _validate_password(pwd)
      _validate_email_address(email)
      fakecid = random.randint(0,4) #TODO temporary hack
      new_user = int(self.db.insert('user', name=name, password=pwd, 
                                email=email, cid0=fakecid, cid1=fakecid,
                                current_batch=1))
      return new_user

    def check_ticket(self, uid, ticket):
        if len(self.db.select('ticket', where='uid=%d and ticket=%s' % (uid, sql_str(ticket)))) == 0:
            return False
        else:
            self.db.update('ticket', where='uid=%d and ticket=%s' %
                       (uid, sql_str(ticket)),
                       last_used=datetime.now().isoformat())
            return True

    def make_ticket(self, uid):
        ticket = str(random.randint(0, 2**128))
        #self.db.insert('ticket', uid=uid, ticket=ticket,
        #           last_used=datetime.now().isoformat())

        self.db.query('insert into ticket (uid, ticket) values (%d, %s)'  % (uid, sql_str(ticket)))
        return ticket
    
    def get_user(self, uid):
        user = self.db.query('select *, cid%d as cid from user where id=%d' % (self.active_cid, uid))
        if len(user) is 0: raise DataError("user with uid %d not found" % uid)

        return user[0]

    def get_uid_from_name(self, name):
        user = self.db.select('user', where='name=%s' % sql_str(name))
        if len(user) is 0: raise DataError("user with name %s not found" % name)
        return int(user[0].id)

    def create_empty_post(self, uid):
        #pid = int(self.db.query('insert into post values (%d, %d, "", 0)') % ()
        pid = int(self.db.insert('post', uid=uid, claim='', broad_support=0))
        return pid

    def fill_out_post(self, pid, uid, claim, content):
        self.db.update('post', where='id=%d and uid=%d' % (pid, uid),
                   claim=claim, content=content)

        self._expose_post(uid, pid, content, 0)

    
    def create_post(self, uid, claim, content):
        pid = int(self.db.insert('post', uid=uid, claim=claim))
        
        self._expose_post(uid, pid, content, 0)
        return pid

    def _expose_post(self, uid, pid, content, b_s=0):
        tokens = ' '.join(self.search.tokens(content))
        self.db.insert('post_content', pid=pid,
                   #these args are automatically sqlquoted?
                   raw=content,  
                   tokens = tokens,
                   safe_html='TODO')
        self.vote(uid, pid)
        self.search.add_article_contents(tokens, pid, b_s)


    
    class LazyPost:
      def __init__(self, state, pid):
        self.state = state
        self.pid = pid
      #TODO: some good lazy DB access.
    #def get_post(self, pid):
    #  return LazyPost(self, pid)

    #TODO: this laziness system works, but is kinda ugly.  We should fix it, above
    def get_post(self, pid, content=False):
        post = self.db.select('post', where='id=%d' % pid)
        if len(post) is 0: raise DataError("article with pid %d not found" % pid)
        if content == False:
            return post[0]

        lazies = {
            'raw' : (lambda : self.db.query('select raw from post_content where pid=%d' % pid)[0].raw),
            'safe_html' : (lambda : self.db.query('select safe_html from post_content where pid=%d' % pid)[0].safe_html),
            #'tokens' : (lambda : self.db.query('select tokens from post_content where pid=%d' % pid)[0].tokens)
            }
            
        lazies.update(post[0])
        
        return web.storage(lazies)

    def inc_batch(self, user):
        self.db.query('update user set latest_batch=%d where id=%d'
                  % (user.latest_batch+1, user.id))

    def add_to_history(self, uid, pid, batch, position):
      #TODO: ensure uniqueness better
      if len(self.db.select('history', where='uid=%d and pid=%d' % (uid, pid))) == 0:
        self.db.insert('history', uid=uid, pid=pid, batch=batch, position=position)


    def get_history(self, uid, batch):
        pids = [s.pid for s in
                self.db.query('select pid from history where uid=%d and batch=%d order by position'
                         % (uid, batch))]

        return [self.get_post(pid, True) for pid in pids]
        

    #TODO: after get_post is fixed, optimize, by going back to grabbing them.
    def get_random_pids(self, count):
        return [p.id for p in self.db.select('post', order='rand()', limit='%d' % count)]

    def vote(self, uid, pid):
        if len(self.db.select('vote', where='uid=%d and pid=%d' % (uid, pid))) == 0:
            self.db.insert('vote', uid=uid, pid=pid)
        # otherwise vote already exists -- do nothing

    def add_term(self, uid, pid, term):
      #TODO: validate term
      if len(self.db.select('relevance', where='uid=%d and pid=%d and term=%s' % (uid, pid, sql_str(term)))) == 0:
        #log_dbg("STATE: vote term: [%s]" % term) #terms are bare
        self.db.insert('relevance', uid=uid, pid=pid, term=term)


    def voted_for(self, uid, pid):
        return len(self.db.select('vote', where='uid=%d and pid=%d' % (uid, pid))) > 0

    def terms_voted_for(self, uid, pid):
        return [entry.term for entry in self.db.query(
          'select term from relevance where uid=%d and pid=%d' % (uid, pid))]

    def update_support(self, pid, support):
        self.db.update('post', where='id=%d' % pid, broad_support=support)
        self.search.update_support(pid, support)

    def dump_votes(self):
        votes = self.db.select('vote')
        return [(vote.uid, vote.pid) for vote in votes]

    def votes_by_uid(self, uid):
        votes = self.db.select('vote', where = 'uid=%d' % uid)
        return votes

    def recent_votes(self, voter, limit):
        return [v.pid for v in
            self.db.query(
              '''select vote.pid from vote
                   where uid=%d
                   order by date_voted desc
                   limit %d''' % (voter, limit))]

    def recent_unviewed_votes(self, voter, viewer, limit):
        #Get votes made by _voter_ for articles _viewer_ hasn't viewed.
        return [v.pid for v in
            self.db.query(
              '''select vote.pid from vote
                   left outer join history
                     on (vote.pid=history.pid and history.uid=%d)
                   where vote.uid=%d and history.uid is null
                   order by vote.date_voted desc
                   limit %d''' % (viewer, voter, limit))]
        # the weird join is there because we care about the *absence* of an appropriate _history_ entry


    def votes_for_pid(self, pid):
        votes = self.db.select('vote', where = 'pid=%d' % pid) 
        if len(votes) is 0: return []
        return votes

    def get_num_clusters(self):
        num_query = self.db.select('vote', what='count(*)')
        num_clusters = num_query[0]['count(*)']
        return num_clusters

    def get_sample_users_in_cluster(self, cluster, count):
        return self.db.query('select *, cid%d as cid from user where cid%d=%d order by rand() limit %d'
                  % (self.active_cid, self.active_cid, cluster, count) )

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
            rec = int(self.db.select('user', what='count(*)',
                          where='cid%d=%d' % (self.active_cid, cluster)
                     )[0]['count(*)'])
            self.cluster_size_cache[cluster] = rec
            return rec

    def get_votes_by_pid_clustered(self, pid):
        self.cluster_count = 5 #TODO update with each rebasing, not here
        
        vote_list = self.db.query('''
        select user.cid%d as cid, count(*) from vote
        inner join user on vote.uid=user.id
        where pid=%d
        group by cid
        ''' % (self.active_cid, pid))
        retval = [0 for c in xrange(self.cluster_count)]
        for record in vote_list:
            retval[record['cid']] = record['count(*)']
        return retval

    def get_term_popularity(self, term):
        log_tmp("STATE: term: [%s]" % term)
        return self.db.query('select count(*) from relevance where term=%s' % sql_str(term))[0]['count(*)']

    def get_term_in_clusters(self, term, clusters):
        log_tmp("STATE: clusters: " + str(clusters))
        #It looks like keyword arguments (like those used in self.db.insert in _vote_())
        #get quoted twice, if used in combination with sqlquote()
        #TODO: force web.py to do it right, rather than matching them
        return [r.pid for r in
            self.db.query('''
                select relevance.pid from relevance
                inner join user on relevance.uid=user.id
                where relevance.term="%s" and user.cid%d in (%s)
                ''' % (
                       sql_str(term),
                       self.active_cid,
                       ', '.join(['%d'%c for c in clusters]))
                      )]

    

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
        return [con.cid_to for con in
           self.db.query('''select cid_to from cluster_connection
                        where cid_from=%d''' % (cluster))]
  
    def connected_cluster_sample(self, cluster, count):
        return [con.cid_to for con in
           self.db.query('''select cid_to from cluster_connection
                        where cid_from=%d
                        order by rand()
                        limit %d''' % (cluster, count))]
    
    def add_callout(self, pid, start, end, voter):
        web.query('insert into callout_votes values (%d, %d, %d, %d)' 
                  % (pid, start, end, voter))
        #TODO handle repeat votes -- update?

    def callouts_for(self, pid):
        return self.db.query('select * from quote where pid=%d' % pid)


the = State()
