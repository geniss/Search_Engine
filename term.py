class Term:
    __slots__ = ['text', 'numOfInterfaces', 'numOfDoc', 'is_entity', 'postings']

    def __init__(self, text):
        self.text = text
        self.numOfInterfaces = 1
        self.numOfDoc = 0  # dfi
        self.is_entity = False
        self.postings = []  # PostingByTerm
