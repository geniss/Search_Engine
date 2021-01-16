# DO NOT MODIFY CLASS NAME
import utils


class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    __slots__ = ['inverted_idx', 'documents', 'config']

    def __init__(self, config):
        self.inverted_idx = set()
        self.documents = set()
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
        self.documents.add(document)
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for word in document_dictionary.keys():
            try:
                # Update inverted index and posting
                word.postings.append((document.tweet_id, document_dictionary[word] / document.max_word))
                self.inverted_idx.add(word)
            except:
                print('problem with the following key {}'.format(word))

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self.inverted_idx, self.documents = utils.load_obj(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.save_obj((self.inverted_idx, self.documents), fn)
