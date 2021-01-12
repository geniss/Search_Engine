# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math


class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_docs, k=None,query_grades=None,):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """

        sum_wq_sqr = sum([a ** 2 for a in query_grades.values()])
        output = []
        for doc in relevant_docs.keys():
            sum_wi_sqr = 0
            score = 0
            for term in relevant_docs[doc].keys():
                sum_wi_sqr += relevant_docs[doc][term] ** 2
                score += query_grades[term] * relevant_docs[doc][term]  # sim()
            if math.sqrt(sum_wi_sqr * sum_wq_sqr)==0:
                s=score /0.001
            else:
                s = score / math.sqrt(sum_wi_sqr * sum_wq_sqr)
            output.append((doc, s))

        sorted_relevant_doc=sorted(output, key=lambda item: item[1], reverse=True)
        if k!=None:
            sorted_relevant_doc=sorted_relevant_doc[:k]
        return [d[0] for d in sorted_relevant_doc]

