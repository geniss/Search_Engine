# DO NOT MODIFY CLASS NAME
import math
import utils


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    __slots__ = ['inverted_idx','postingDict','config']
    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = config

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for word in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if word.text not in self.inverted_idx.keys():
                    word.numOfDoc += 1
                    self.inverted_idx[word.text] = []
                    self.postingDict[word.text]=[]
                self.postingDict[word.text].append((document.tweet_id, document_dictionary[word]/document.max_word))
            except:
                print('problem with the following key {}'.format(word[0]))


        # sigma,tfi = 0
        # for word in document_dictionary:
        #     tfi=document_dictionary[word]/document.max_word
        #     self.inverted_idx[word] = tfi
        #     sigma += tfi**2
        #
        # if sigma != 0:
        #     sigma = 1 / math.sqrt(sigma)
        #
        # for word in document_dictionary:
        #     self.inverted_idx[word][0][0] *= sigma

    def CreatInvertedIndex(self,word_dict, idx,global_table=None):
        n=idx+1
        for word in list(word_dict.keys()):

            word = (word, word_dict.pop(word))
            if word[1].numOfDoc < 2:
                self.inverted_idx[word[0]] = None
            elif word[1].is_entity and word[1].numOfDoc < 2:
                self.inverted_idx[word[0]] = None
            else:
                self.inverted_idx[word[0]]=[0,math.log2(n / word[1].numOfDoc)]
        return self.inverted_idx


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        utils.save_obj(self.inverted_idx, fn)


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.load_obj(fn)


    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return self.inverted_idx.keys().__contains__(term)


    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        if term not in self.postingDict.keys():
            return []

        return self.postingDict[term]
