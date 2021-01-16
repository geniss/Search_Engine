import json
import math
import re
import string

from nltk.corpus import stopwords
from spellchecker import SpellChecker

from document import Document
from stemmer import Stemmer
from term import Term


class Parse:
    __slots__ = ['word_dict', 'stemmer', 'stop_words', 'rules', 'spell', 'min_length']

    def __init__(self, config):
        self.word_dict = {}
        self.stemmer = Stemmer(config.stemming)
        self.stop_words = [self.stemmer.stem_term(word) for word in stopwords.words('english')] + ['rt', 't.co',
                                                                                                   'https']
        self.rules = config.parser_rules
        self.spell = SpellChecker()
        self.min_length = config.min_length

    # helper function for numberTostring-->return 3 digit after the point
    @staticmethod
    def round_down(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier

    @staticmethod
    def isNumber(word):
        return '0' <= word[0] <= '9'

    def numberToString(self, num):
        if num < 1000:
            return str(num)
        elif 1000 <= num < 1000000:
            num = num / 1000
            num = self.round_down(num, 3)
            if num == int(num):
                num = int(num)
            s = str(num)
            return s + 'K'
        elif 1000000 <= num < 1000000000:
            num = num / 1000000
            num = self.round_down(num, 3)
            if num == int(num):
                num = int(num)
            s = str(num)
            return s + 'M'
        else:
            num = num / 1000000000
            num = self.round_down(num, 3)
            if num == int(num):
                num = int(num)
            s = str(num)
            return s + 'B'

    # This function is "cleaning" the word,removing a ,!@$&*... that appear in start/end of word
    @staticmethod
    def strip_punctuations(word):
        if word == '$':
            return word
        start = 0
        end = len(word) - 1
        while start < len(word) and word[start] in (string.punctuation + '\n\t'):
            if word[start] == '@' or word[start] == '#' or word[start] == '"':
                break
            start += 1
        while end >= 0 and word[end] in string.punctuation:
            if word[end] == '"' or word[end] == '$':
                break
            end -= 1
        return word[start:end + 1]

    # This function clean the text-->remove if not exist in ascii table
    @staticmethod
    def removeEmojis(text):
        return text.encode('ascii', 'ignore').decode('ascii')

    # #stayAtHome--->['#stayAtHome', 'stay', 'At',Home]
    @staticmethod
    def hashtag(term):
        res = [term]
        start = 1
        for i in range(2, len(term)):
            if term[i].isupper():
                res.append(term[start:i])
                start = i
        res.append(term[start:])
        return res

    @staticmethod
    def URL(text):
        return [v for v in re.split('[://]|[/?]|[/]|[=]', text) if v]

    @staticmethod
    def extendURLs(document):
        url_map = json.loads(document[3])
        url_indices = json.loads(document[4])
        full_text = document[2]
        offset = 0
        for index in url_indices:
            try:
                new_offset = offset + len(url_map[full_text[(index[0] + offset):(index[1] + offset)]]) - index[1] + \
                             index[0]
                full_text = full_text[:(index[0] + offset)] + url_map[
                    full_text[(index[0] + offset):(index[1] + offset)]] + full_text[(index[1] + offset):]
                offset = new_offset
            except:
                pass
        document[2] = full_text

    @staticmethod
    def add_or_inc(d, term):
        if not term:
            return
        elif term not in d:
            d[term] = 0
        d[term] += 1

    def add_to_dict(self, word):
        low_case = word.lower()
        if low_case in self.stop_words:
            return None
        if len(low_case) < self.min_length:
            return None
        if self.rules['capitals']:
            if low_case in self.word_dict.keys():
                if word == low_case:
                    self.word_dict[low_case].text = low_case
            else:
                self.word_dict[low_case] = Term(word)
        else:
            if low_case not in self.word_dict.keys():
                self.word_dict[low_case] = Term(low_case)
        return self.word_dict[low_case]

    def add_entity_to_dict(self, word):
        low_case = word.lower()
        if low_case in self.stop_words:
            return None
        if low_case in self.word_dict.keys():
            self.word_dict[low_case].numOfInterfaces += 1
            if word == low_case:
                self.word_dict[low_case].text = low_case
        else:
            self.word_dict[low_case] = Term(word)
            self.word_dict[low_case].is_entity = True
        return self.word_dict[low_case]

    def Tokenize(self, text):
        output = {}
        if self.rules['spellcheck']:
            word_list = [self.spell.correction(word) for word in
                         [self.stemmer.stem_term(self.strip_punctuations(word)) for word in text.split()]
                         if word]
        else:
            word_list = [word for word in
                         [self.stemmer.stem_term(self.strip_punctuations(word)) for word in text.split()]
                         if word]

        size = len(word_list)

        # find all the quotes in this doc
        # re.findall() find all quotes and return a list of quotes without " "
        if self.rules['quotes']:
            quotes = [self.add_to_dict('"{}"'.format(quote)) for quote in re.findall(r'"(.*?)"', text)]
            for q in quotes:
                self.add_or_inc(output, q)

        # The main loop
        for i in range(size):
            word = word_list[i]

            if self.rules['entity']:
                if (i + 1) < size and 'A' <= word[0] <= 'Z' and 'A' <= word_list[i + 1][0] <= 'Z':
                    j = i + 2
                    entity = word + ' ' + word_list[i + 1]
                    self.add_or_inc(output, self.add_entity_to_dict(entity))
                    while j < size and 'A' <= word_list[j][0] <= 'Z':
                        entity = entity + ' ' + word_list[j]
                        self.add_or_inc(output, self.add_entity_to_dict(entity))
                        j += 1
            if self.rules['less_more']:
                if (i + 1) < size and word.lower() in ['less', 'more']:
                    new_term = f'{word} {word_list[i + 1]}'
                    if word_list[i + 1].lower() == 'than' and i + 2 < size:
                        new_term += f' {word_list[i + 2]}'
                    self.add_or_inc(output, self.add_to_dict(new_term.lower()))
            if self.isNumber(word):
                if self.rules['number']:
                    try:
                        if i + 1 < size and word_list[i + 1].lower() in [self.stemmer.stem_term('percent'),
                                                                         self.stemmer.stem_term('percentage')]:
                            i += 1
                            word += '%'

                        elif i + 1 < size and word_list[i + 1].lower() in [self.stemmer.stem_term('dollar'),
                                                                           self.stemmer.stem_term('dollars')]:
                            i += 1
                            word += '$'

                        # check if the number is actually separate to 2 word: 35 3/5
                        elif i + 1 < size and self.isNumber(word_list[i + 1]) and '/' in word_list[i + 1]:
                            word += ' ' + word_list[i + 1]
                        # cases of Thousand=K    Million=M    Billion=B--->the function numberToString do it
                        elif i + 1 < size and word_list[i + 1].lower() == self.stemmer.stem_term('thousand'):
                            i += 1
                            word = self.numberToString(float(word) * 1000)
                        elif i + 1 < size and word_list[i + 1].lower() == self.stemmer.stem_term('million'):
                            i += 1
                            word = self.numberToString(float(word) * 1000000)
                        elif i + 1 < size and word_list[i + 1].lower() == self.stemmer.stem_term('billion'):
                            i += 1
                            word = self.numberToString(float(word) * 1000000000)
                        else:
                            word = self.numberToString(float(word))
                    except:
                        pass
                    self.add_or_inc(output, self.add_to_dict(word))
            # hashtag
            elif word[0] == '#':
                if self.rules['hashtag']:
                    for word in self.hashtag(word):
                        self.add_or_inc(output, self.add_to_dict(word))
            # URL
            elif word[0:4] == "http":
                if self.rules['url']:
                    for word in self.URL(word):
                        self.add_or_inc(output, self.add_to_dict(word))

            # Tag
            elif word[0] == '@':
                if self.rules['tag']:
                    self.add_or_inc(output, self.add_to_dict(word))
            else:
                self.add_or_inc(output, self.add_to_dict(word))
        return output

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presetting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]

        if self.rules['ext_url']:
            self.extendURLs(doc_as_list)
            full_text = doc_as_list[2]

        if self.rules['emoji']:
            full_text = self.removeEmojis(full_text)

        full_text = full_text.replace('\n', ' ')

        term_dict = self.Tokenize(full_text)

        doc_length = sum(term_dict.values())

        max_word = max(term_dict.values())

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, max_word)
        return document
