class Doc:
    def __init__(self, url, length, startPos=0):
        self.url = url
        self.length = length
        self.startPos = startPos


class Word:
    def __init__(self, numDocs=0, positions=[]):
        self.numDocs = numDocs  # number of documents that this word appears in
        self.positions = positions
