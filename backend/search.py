import xapian
from reverend.thomas import Bayes

import state

#Search strategy: For each search term, we cast around nearby clusters
#for the nearest people to have made such a search before.  We train a
#bayesian classifier based on those results, and then do a fulltext
#search to find articles that are likely to score high in relevance.
#Then we filter those results down by score, if applicable.

# the only special search feature we want is probably phrasing (possibly autophrasing)

class Search:
    def __init__(self):
        self.guesser = Bayes()
        self.mainabase = xapian.WritableDatabase('yb-search', xapian.DB_CREATE_OR_OPEN)

        indexer = xapian.TermGenerator()
        self.stemmer = xapian.Stem("english") #I18N
        indexer.set_stemmer(self.stemmer)

        self.term_cache = () #is this the right way to init a hash?
            
    #Term must be normalized and stemmed and everything first
    def get_term_exemplars(self, cid, term):
        goal_count = math.ceil(math.sqrt(state.get_term_popularity(term)))
        
        scope = set()
        results = []
        scope.add(cid)
        scope_edge = set()
        scope_edge.add(cid)

        distance = 0
        #sweep out further and further away until we get enough examples
        while len(results) < goal_count and len(scope_edge) != 0:
            new_scope_edge = set()
            for c in scope_edge:
                new_scope_edge |= state.connected_clusters(c)

            new_scope_edge -= scope
            results += state.get_term_in_clusters(new_scope_edge)

            scope_edge = new_scope_edge

    def local_search(self, cid, term, recent, count):
        exemplar_pids = self.get_term_exemplars(cid, term)
        guesser = Bayes()
        #TODO use cache
        for ex_pid in exemplar_pids:
            ex = state.get_post(ex_pid, content=True)

            guesser.train("relevant", ex.tokens()) #get normalized content from p.
            # TODO Toss in other factors, if possible.

        for neg_ex in state.get_random_posts(len(exemplar_pids)):
            guesser.train("random", neg_ex.tokens())

        proportions = [
            (tok, count / (1.0 * guesser.pools["random"][tok]))
                for (tok, count) in guesser.poolData("relevant")
        ]

        proportions = [ #knock out the weak and irrelevant ones before sorting
            (tok, prop) for (tok, prop) in proportions if prop > 1.15 ]

        if len(proportions) <= 2:
            pass #TODO revert to fulltext search

        sort(proportions, key=operator.itemgetter(1), reverse=True)

        #search for the eight best words
        query = xapian.Query(xapian.Query.OP_OR, [ tok for (tok, prop) in proportions[:8]] )

        self.term_cache[term] = (query, guesser)

        #TODO: we want to mix in an absolute quality score at this point.
        #Can Xapian do that?
        enq = xapian.Enquire(self.mainabase)
        enq.set_query(query)
        mset = enq.get_mset(0, int(count*2.5))

        scored_results = [ (m, 1) for m in mset ] #TODO: get score and extract pid
        sort(scored_results, key=operator.itemgetter(1))

        return scored_results[:count] #TODO extract pids
                              


    def add_article(self, post):
        doc = xapian.Document()
        doc.set_data(post.contents)

        indexer.set_document(doc)
        indexer.index_text(post.tokens)

        self.mainabase.add_document(doc)

    


    
