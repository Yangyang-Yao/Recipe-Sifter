#!/usr/bin/python3

import sys
from collections import defaultdict
from preprocess import Preprocessor
from common import Word, Doc


class Solver:
    def __init__(self, indexFile, docsFile, pageRankFile):
        self.preprocessor = Preprocessor()

        # 'word' -> Word
        self.index = defaultdict(Word)

        # docId -> Doc
        self.docIndex = defaultdict(Doc)

        # position -> docId
        self.docList = []

        # url -> rank
        self.pageRanks = {}

        self.initIndex(indexFile)
        self.initDocs(docsFile)
        self.initPageRanks(pageRankFile)


    def initIndex(self, indexFile):
        with open(indexFile, 'r') as fopen:
            for line in fopen:
                splitted = line.rstrip().split(' ')
                word = splitted[0]
                numDocs = int(splitted[1])
                positions = []

                for i in range(2, len(splitted)):
                    pos = int(splitted[i])
                    positions.append(pos)
                
                self.index[word] = Word(numDocs, positions)


    def initDocs(self, docsFile):
        with open(docsFile, 'r') as fopen:
            totalLength = 0
            for line in fopen:
                docId, url, length = line.rstrip().split(' ')
                docId = int(docId)
                length = int(length)
                self.docIndex[docId] = Doc(url, length, totalLength)
                for i in range(length):
                    self.docList.append(docId)
                    totalLength += 1
    

    def initPageRanks(self, pageRankFile):
        with open(pageRankFile, 'r') as fopen:
            for line in fopen:
                url, rank = line.rstrip().split(' ')
                self.pageRanks[url] = float(rank)
    
    
    def solve(self, query):
        matches = set()
        queryWords = self.preprocessor.preprocess(query)
        for word in queryWords:
            if word not in self.index:
                continue
            
            positions = self.index[word].positions
            for pos in positions:
                docId = self.docList[pos]
                matches.add(docId)
        
        rankedMatches = self.rank(query, matches)
        return rankedMatches

    
    def rank(self, query, matches):
        queryWords = self.preprocessor.preprocess(query)
        scores = []
        for match in matches:
            doc = self.docIndex[match]
            score = 0
            foundWords = [False] * len(queryWords)
            for i, word in enumerate(queryWords):
                if word not in self.index:
                    continue
                    
                positions = set(self.index[word].positions)
                for j in range(doc.length):
                    pos = doc.startPos + j
                    if pos in positions:
                        foundWords[i] = True
                        break
            
            for i, found in enumerate(foundWords):
                if found:
                    score += 10
                    if i > 0 and foundWords[i - 1]:
                        score += 20

            score += self.pageRanks[doc.url] * 10000
            scores.append((match, score))
        
        sortedDocs = sorted(scores, key=lambda x: x[1], reverse=True)
        rankedMatches = []
        for doc in sortedDocs:
            docId = doc[0]
            docUrl = self.docIndex[docId].url
            rankedMatches.append((docUrl, doc[1]))
        return rankedMatches


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: solver.py <index-file> <docs-file> <page-rank-file> <query>')
    else:
        indexFile = sys.argv[1]
        docsFile = sys.argv[2]
        pageRankFile = sys.argv[3]
        query = sys.argv[4]
        solver = Solver(indexFile, docsFile, pageRankFile)
        matches = solver.solve(query)
        for match in matches:
            print(f'{match[1]} {match[0]}')
