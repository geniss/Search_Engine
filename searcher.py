import math

from nltk.corpus import lin_thesaurus as thes
from nltk.corpus import wordnet
from spellchecker import SpellChecker

from ranker import Ranker


# DO NOT MODIFY CLASS NAME
class Searcher:
    __slots__ = ['_parser', '_indexer', '_ranker', '_the_count', '_model', '_min_relevant', '_ext_val',
                 '_wordnet_count']

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, config, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker(config)
        self._model = model
        self._the_count = config.the_count
        self._wordnet_count = config.wordnet_count
        self._min_relevant = config.min_relevant
        self._ext_val = config.ext_val

    def CalculateW(self, query, extenders):
        output = {term: 1 for term in query}
        for term in extenders:
            if term not in output:
                output[term] = 0
            output[term] += self._ext_val
        return output

    def wordNet(self, word):
        syn = set()
        for syn_set in wordnet.synsets(word):
            for lemma in syn_set.lemmas():
                syn.add(lemma.name())
                if lemma.antonyms():
                    syn.add(lemma.antonyms()[0].name())
                if len(syn) >= self._wordnet_count:
                    return syn
        return syn

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None, methods=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relevant
            and the last is the least relevant result.
        """

        # spell corrections
        if 1 in methods:
            spell = SpellChecker()
            query = ' '.join([spell.correction(word) for word in query.split()])

        query_terms = self._parser.Tokenize(query).keys()
        extenders = set()

        # wordNet
        if 2 in methods:
            for word in query_terms:
                for ex_word in self.wordNet(word.text):
                    extenders.add(self._parser.add_to_dict(ex_word))

        # lin_thesaurus
        if 3 in methods:
            for word in query_terms:
                for ex_word in list(thes.synonyms(word.text)[1][1])[:self._the_count]:
                    extenders.add(self._parser.add_to_dict(ex_word))

        extenders = {extender for extender in extenders if extender}
        w_of_term_in_query = self.CalculateW(query_terms, extenders)

        relevant_docs = self._relevant_docs_from_posting(w_of_term_in_query.keys())
        ranked_doc_ids = self._ranker.rank_relevant_docs(relevant_docs, k, w_of_term_in_query)

        return len(ranked_doc_ids), ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_terms):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_terms: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for term in query_terms:
            if len(term.postings) == 0:
                continue
            idf = math.log2(len(term.postings) / len(self._indexer.documents))
            for doc_id, tf in term.postings:
                if doc_id not in relevant_docs.keys():
                    relevant_docs[doc_id] = {}
                relevant_docs[doc_id][term] = tf * idf  # wiq

        return {doc: relevant_docs[doc] for doc in relevant_docs if len(relevant_docs[doc]) >= min(self._min_relevant, len(query_terms))}
