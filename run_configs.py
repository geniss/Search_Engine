class RunConfigClass:
    def __init__(self, stemming=False, ext_url=True, emoji=True, quotes=False, entity=False,
                 less_more=True, number=True, hashtag=True, url=True, tag=True, capitals=False, spellcheck=False,
                 min_length=1, min_relevant=1, the_count=4, wordnet_count=4, min_occurrence=3, ext_val=0.1,
                 cos_sym=True):
        self.stemming = stemming
        self.parser_rules = {'ext_url': ext_url, 'emoji': emoji, 'quotes': quotes,
                             'entity': entity, 'less_more': less_more, 'number': number, 'hashtag': hashtag, 'url': url,
                             'tag': tag, 'capitals': capitals, 'spellcheck': spellcheck}
        self.min_length = min_length
        self.min_occurrence = min_occurrence
        self.min_relevant = min_relevant
        self.the_count = the_count
        self.wordnet_count = wordnet_count
        self.ext_val = ext_val
        self.cos_sym = cos_sym

    def toString(self):
        return f'stemming: {self.stemming}, ' \
               f'parser_rules: {self.parser_rules}, ' \
               f'min_length: {self.min_length}, ' \
               f'min_occurrence: {self.min_occurrence}, ' \
               f'min_relevant: {self.min_relevant}, ' \
               f'wordnet_count: {self.wordnet_count}, ' \
               f'ext_val: {self.ext_val}, ' \
               f'cos_sym: {self.cos_sym}, ' \
               f'the_count: {self.the_count}'
