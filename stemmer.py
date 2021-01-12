from nltk.stem.porter import PorterStemmer


class Stemmer:
    __slots__ = ['stemmer', 'do_stem']

    def __init__(self, do_stem):
        self.stemmer = PorterStemmer()
        self.do_stem = do_stem

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        if not self.do_stem:
            return token
        else:
            word = str(token)
            if word == word.title():
                word = self.stemmer.stem(word).capitalize()
            elif word.isupper():
                word = self.stemmer.stem(word).upper()
            else:
                word = self.stemmer.stem(word)
            return word
