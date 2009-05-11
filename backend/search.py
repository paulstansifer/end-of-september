import math
import operator
import random
from datetime import timedelta, datetime

import xapian
from reverend.thomas import Bayes

import state
from frontend.log import *


#Search strategy: For each search term, we cast around nearby clusters
#for the nearest people to have made such a search before.  We train a
#bayesian classifier based on those results, and then do a fulltext
#search to find articles that are likely to score high in relevance.
#Then we filter those results down by score, if applicable.

# the only special search feature we want is probably phrasing (possibly autophrasing)

DOC_PID = 0
BROAD_SUPPORT = "B"


def _post_age_score(post):
    age = datetime.now() - post.date_posted
    age_hours = age.days*24.0 + age.seconds/(60.0*60)
    return 1 / math.sqrt(age_hours) #more recent is better, but it falls off

class SearchResult:
    def __init__(self, post, term, score):
        self.post = post
        self.term = term
        self.score = score

class Search:
    def __init__(self, db_name):
        self.guesser = Bayes()
        self.name = db_name+'-search'
        self.mainabase = xapian.WritableDatabase(self.name, xapian.DB_CREATE_OR_OPEN)

        self.indexer = xapian.TermGenerator()
        self.stemmer = xapian.Stem("english") #I18N
        self.indexer.set_stemmer(self.stemmer)

    def close(self):
        self.mainabase = None

    def clear(self):
        self.mainabase = None
        self.mainabase = xapian.WritableDatabase(self.name, xapian.DB_CREATE_OR_OVERWRITE)

    def stem(self, word):
        return self.stemmer(word.lower())

    def tokens(self, text):
        words = text.split() #just by whitespace, so far
        ret_val = []
        for word in words:
            ret_val.append(self.stem(word))
        return ret_val

    #exemplars are documents that are well-related to the given search
    #term, as determined by tagging ("worth the read for"...)

    #Term must be normalized and stemmed and everything first
    def get_term_exemplars(self, cid, term):
        popularity = state.the.get_term_popularity(term)
        
        goal_count = min(int(math.ceil(math.sqrt(popularity)))*2, popularity)


        scope = set()
        results = []
        scope.add(cid)
        scope_edge = set()
        scope_edge.add(cid)

        distance = 0

        print >> sys.stderr, "EXEMPLARS: ", len(results), " < ", goal_count, " ... ", len(scope_edge)
        #sweep out further and further away until we get enough examples
        while len(results) < goal_count and len(scope_edge) != 0:
            new_scope_edge = set()
            for c in scope_edge:
                new_scope_edge |= set(state.the.connected_clusters(c))

            new_scope_edge -= scope
            results += state.the.get_term_in_clusters(term, new_scope_edge)
            print >> sys.stderr, "EXEMPLARS: ", state.the.get_term_in_clusters(term, new_scope_edge)


            scope_edge = new_scope_edge
            #print >> sys.stderr, "EXEMPLARS: ", len(results), " < ", goal_count, " ... ", len(scope_edge)

        random.shuffle(results)

        return results[:goal_count]


    def local_search(self, cid, term_unstemmed, recent):
        term = self.stem(term_unstemmed)
        exemplar_pids = self.get_term_exemplars(cid, term)
        if len(exemplar_pids) < 4:
            return self.fulltext(cid, term, recent)

        log_tmp("SEARCH: %s exemplars" % len(exemplar_pids))
        
        guesser = Bayes()

        for ex_pid in exemplar_pids:
            ex = state.the.get_post(ex_pid, content=True)
            log_tmp( "SEARCH: exemplar tokens: [%s]" % ex.tokens())
            guesser.train("relevant", ex.tokens()) #get normalized content from p.
            # TODO Toss in other factors, if possible.

        for neg_ex_pid in state.the.get_random_pids(len(exemplar_pids)): #probably cacheable, if we use a bigger pool
            guesser.train("random", state.the.get_post(neg_ex_pid, content=True).tokens())

        log_tmp("SEARCH: trained")

        proportions = [
            (tok, (count+1) / (1.0 * guesser.pools["random"].get(tok,0) + 1))
                for (tok, count) in guesser.poolData("relevant")
        ]

        proportions = [ #knock out the weak and irrelevant ones before sorting
            (tok, prop) for (tok, prop) in proportions if prop > 2 ]

        fulltext_fallback = len(proportions) < 3

        if fulltext_fallback:
            query = xapian.Query(xapian.Query.OP_AND, [term])
        else:
            proportions.sort(key=operator.itemgetter(1), reverse=True)
            log_tmp("SEARCH: proportions: " + str(proportions))
            #search for the twelve best words
            query = xapian.Query(xapian.Query.OP_OR, [ tok for (tok, prop) in proportions[:12]] )

        log_tmp("SEARCH: query: " + str(query))

        enq = xapian.Enquire(self.mainabase)
        enq.set_query(
#            xapian.Query(xapian.Query.OP_AND,
                query
#                , ##Something scoring for BROAD_SUPPORT##)
                ##Something scoring for recency, if appropriate
            )
        mset = enq.get_mset(0, 25)

        results = []
        for m in mset:
            doc = m.get_document()
            post = state.the.get_post(int(doc.get_data()), True)
            
            for (pool, prob) in guesser.guess(post.tokens()):
                if pool == "relevant":
                    rel_prob = prob
            score = rel_prob
            score *= post.broad_support
            if recent:
                score *= _post_age_score(post)
            results.append(SearchResult(post, term, score))
            #results.append( (post, score, "rel: %f  b_s: %f  root age: %f" %
            #                 (rel_prob, post.broad_support, sqrt(age_days)) ) )
        results.sort(lambda x,y: cmp(x.score, y.score), reverse=True)
        return results[:10]

    def fulltext(self, cid, term, recent):
        log_tmp("SEARCH:FULLTEXT")
        enq = xapian.Enquire(self.mainabase)
        query = xapian.Query(xapian.Query.OP_OR, [term])
        enq.set_query(query)
        mset = enq.get_mset(0, 25)

        results = []
        for m in mset:
            doc = m.get_document()
            post = state.the.get_post(int(doc.get_data()), True)

            score = m.get_percent()
            score *= post.broad_support
            if recent:
                score *= _post_age_score(post)
            results.append(SearchResult(post, term, score))
            #results.append( (post, score, "rel: %f  b_s: %f  root age: %f" %
            #                 (rel_prob, post.broad_support, sqrt(age_days)) ) )
        results.sort(lambda x,y: cmp(x.score, y.score), reverse=True)

        return results[:10]
        
        
    def add_article_contents(self, post_tokens, post_id, score):
        doc = xapian.Document()
        doc.set_data(str(post_id))
        doc.add_value(DOC_PID, str(post_id))

        self.indexer.set_document(doc)
        self.indexer.index_text(post_tokens)

        self.mainabase.add_document(doc)

    def update_support(self, pid, score):
        pass #TODO retrieve document and change its score.

