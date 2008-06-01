import xapian
from reverend.thomas import Bayes
import math
import state
import operator
import sys #TMP (debugging output)
import random

#Search strategy: For each search term, we cast around nearby clusters
#for the nearest people to have made such a search before.  We train a
#bayesian classifier based on those results, and then do a fulltext
#search to find articles that are likely to score high in relevance.
#Then we filter those results down by score, if applicable.

# the only special search feature we want is probably phrasing (possibly autophrasing)

DOC_PID = 0
BROAD_SUPPORT = "B"


class Search:
    def __init__(self):
        self.guesser = Bayes()
        self.mainabase = xapian.WritableDatabase('yb-search', xapian.DB_CREATE_OR_OPEN)

        indexer = xapian.TermGenerator()
        self.stemmer = xapian.Stem("english") #I18N
        indexer.set_stemmer(self.stemmer)

    def tokens(self, text):
        words = text.split() #just by whitespace, so far
        ret_val = []
        for word in words:
            ret_val.append(self.stemmer(word.lower()))
        return ret_val
        
    #Term must be normalized and stemmed and everything first
    def get_term_exemplars(self, cid, term):
        goal_count = int(math.ceil(math.sqrt(state.the.get_term_popularity(term))))

        print >> sys.stderr, "EXEMPLARS: pop: %d  goal %d" % (state.the.get_term_popularity(term), goal_count)

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

            scope_edge = new_scope_edge
            print >> sys.stderr, "EXEMPLARS: ", len(results), " < ", goal_count, " ... ", len(scope_edge)

        random.shuffle(results)

        return results[:goal_count]

    def local_search(self, cid, term, recent):
        exemplar_pids = self.get_term_exemplars(cid, term)
        if len(exemplar_pids) < 4:
            pass #TODO revert to fulltext search

        print >> sys.stderr, "SEARCH: %s exemplars" % len(exemplar_pids)
        
        guesser = Bayes()

        for ex_pid in exemplar_pids:
            ex = state.the.get_post(ex_pid, content=True)

            guesser.train("relevant", ex.tokens()) #get normalized content from p.
            # TODO Toss in other factors, if possible.

        for neg_ex_pid in state.the.get_random_pids(len(exemplar_pids)): #probably cacheable, if we use a bigger pool
            guesser.train("random", state.the.get_post(neg_ex_pid, content=True).tokens())

        print >> sys.stderr, "SEARCH: trained"

        proportions = [
            (tok, count / (1.0 * guesser.pools["random"][tok]))
                for (tok, count) in guesser.poolData("relevant")
        ]

        proportions = [ #knock out the weak and irrelevant ones before sorting
            (tok, prop) for (tok, prop) in proportions if prop > 1.15 ]

        print >> sys.stderr, "SEARCH: proportions: ", proportions

        if len(proportions) < 3:
            pass #TODO revert to fulltext search

        proportions.sort(key=operator.itemgetter(1), reverse=True)

        print >> sys.stderr, "SEARCH: props sorted"

        #search for the eight best words
        query = xapian.Query(xapian.Query.OP_OR, [ tok for (tok, prop) in proportions[:8]] )

        enq = xapian.Enquire(self.mainabase)
        enq.set_query(
#            xapian.Query(xapian.Query.OP_AND,
                query
#                , ##Something scoring for BROAD_SUPPORT##)
            )
        mset = enq.get_mset(0, 25)

        print >> sys.stderr, "SEARCH: mset: ", mset
        #TODO: do something with the results
        #use relevance, (optionally) recency, and locality to score

    def add_article(self, post, score):
        doc = xapian.Document()
        doc.set_data(post.id)
        doc.add_value(DOC_PID, str(post.id))
        

        indexer.set_document(doc)
        indexer.index_text(post.tokens)

        self.mainabase.add_document(doc)

    def update_support(self, pid, score):
        pass #TODO retrieve document and change its score.

the = Search()

