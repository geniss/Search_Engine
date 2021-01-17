class Term:
    __slots__ = ['text', 'numOfInterfaces', 'numOfDoc', 'is_entity', 'postings']

    def __init__(self, text):
        self.text = text
        self.numOfInterfaces = 1
        self.is_entity = False
        self.postings = []  # PostingByTerm
