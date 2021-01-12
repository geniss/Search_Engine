from nltk.corpus import wordnet
from spellchecker import SpellChecker
from ranker import Ranker
from nltk.corpus import lin_thesaurus as thes
import utils


# DO NOT MODIFY CLASS NAME
class Searcher:
    __slots__ = ['_parser','_indexer','_ranker','_model']
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model


    def CalculateW(self, query,sourc_words):
        output = {}
        max_term = 0
        for word in query:
            if word not in self._indexer.inverted_idx.keys():
                print("Term {} not found".format(word))
            else:
                if word in output.keys():
                    output[word] += 1
                else:
                    output[word] = 1
                max_term = max(max_term, output[word])

        for word in output.keys():
                if self._indexer.inverted_idx[word] is None or self._indexer.inverted_idx[word] == []:
                    continue
                output[word] = (output[word] / max_term) * self._indexer.inverted_idx[word][1]  # wiq=tf*idf

                if word not in sourc_words and word in query:
                    output[word] *= 0.5
        return output


    def wordNet(self,word):
        syn = list()
        numberOfWords = 0
        for synset in wordnet.synsets(word):
            for lemma in synset.lemmas():
                if numberOfWords <= 5  and lemma.name() not in syn:
                    if lemma.name() in self._indexer.inverted_idx.keys():
                        syn.append(lemma.name())
                        numberOfWords += 1
                if numberOfWords <= 5 :
                    if lemma.antonyms() and (
                            lemma.name not in syn):  # When antonyms are available, add them into the list
                        if lemma.antonyms()[0].name() in self._indexer.inverted_idx.keys():
                            syn.append(lemma.antonyms()[0].name())
                            numberOfWords += 1
        return syn


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None,method=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        p = self._parser
        query_as_list = [term.text.lower() for term in p.parse_sentence(query)]
        surce = query

        #spell corrections
        if method == 1 or method==4:
            spell = SpellChecker()
            for i in range(len(query_as_list)):
                corret = spell.correction(query_as_list[i])
                if corret in self._indexer.inverted_idx.keys():
                    query_as_list[i] = corret

        #wordNet
        elif method == 2 or method==4:
            for word in query_as_list:
                wn = self.wordNet(word)
                for w in wn:
                    if w not in wn:
                        query_as_list += w


        #lin_thesaurus
        elif method == 3 or method==4:
            listi=[]
            for word in query_as_list:
                dic = thes.synonyms(word)[1][1]
                temp = min(len(dic),5)
                cunter=0
                for w in dic:
                    if cunter==temp:
                        break
                    if w in self._indexer.inverted_idx.keys() and len(w)>1:
                        listi.append(w)
                        cunter += 1
            query_as_list+=listi





        w_of_term_in_query=self.CalculateW(query_as_list,surce)

        relevant_docs = self._relevant_docs_from_posting(list(w_of_term_in_query.keys()))
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs,None,w_of_term_in_query)

        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for term in query_as_list:
            post=self._indexer.get_term_posting_list(term)
            posting_list = self._indexer.get_term_posting_list(term)
            for doc_id, tf in posting_list:
                if doc_id not in relevant_docs.keys():
                    relevant_docs[doc_id] = {}
                    if self._indexer.inverted_idx[term] is None or self._indexer.inverted_idx[term]==[]:
                        continue
                    relevant_docs[doc_id][term] = tf * self._indexer.inverted_idx[term][1]  # wiq

        return relevant_docs


