#!/usr/bin/python3

import sys
from collections import defaultdict
from random import shuffle


class PageRank:
    def __init__(self, urlFile, linkFile, convergenceThreshold):
        self.linkFile = linkFile
        self.convergenceThreshold = convergenceThreshold
        self.numUrls = 0

        # takes url -> index in pagerank vector
        self.urlIndicies = defaultdict(int)

        # takes index -> url
        self.urls = defaultdict(str)

        # takes url index -> list of inbound links (indexes)
        self.inUrls = defaultdict(list)

        # takes url index -> list of outbound links (indexes)
        self.outUrls = defaultdict(list)

        self.getUrls(urlFile)
        self.buildGraph(linkFile)

    
    def getUrls(self, urlFile):
        with open(urlFile, 'r') as fopen:
            for rawUrl in fopen:
                index = self.numUrls
                url = rawUrl.strip()
                self.urls[index] = url
                self.urlIndicies[url] = index
                self.numUrls += 1
    

    def buildGraph(self, linkFile):
        with open(linkFile, 'r') as fopen:
            for line in fopen:
                if not line:
                    continue

                try:
                    url, link = line.strip().split(' ')
                except:
                    # throws error when line is blank,
                    # even though I skip blank lines...
                    pass

                # skip links not in 2000
                if link not in self.urlIndicies:
                    continue

                urlIndex = self.urlIndicies[url]
                linkIndex = self.urlIndicies[link]

                self.outUrls[urlIndex].append(linkIndex)
                self.inUrls[linkIndex].append(urlIndex)


    def pagerank(self):
        d = 0.85
        ranks = [0.25] * self.numUrls
        indicies = [i for i in range(self.numUrls)]

        keepIterating = True
        numIterations = 0
        while keepIterating:
            keepIterating = False
            numIterations += 1
            shuffle(indicies)

            for index in indicies:
                prevRank = ranks[index]
                sum = 0
                for inUrl in self.inUrls[index]:
                    sum += ranks[inUrl] / len(self.outUrls[inUrl])
                
                rank = (1 - d) / self.numUrls + d * sum
                ranks[index] = rank

                if abs(prevRank - rank) > self.convergenceThreshold:
                    keepIterating = True
        
        print('Number of iterations: ' + str(numIterations))

        # vector with (url, rank)
        urlRanks = []
        for index, rank in enumerate(ranks):
            urlRanks.append((self.urls[index], rank))

        # sort by rank
        urlRanks.sort(key=lambda x: x[1], reverse=True)

        with open('pagerank.output', 'w') as fopen:
            for url, rank in urlRanks:
                fopen.write(url + ' ' + str(rank) + '\n')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: pagerank.py <url-file> <link-file> <convergence-threshold>')
    else:
        urlFile = sys.argv[1]
        linkFile = sys.argv[2]
        convergenceThreshold = float(sys.argv[3])
        pagerank = PageRank(urlFile, linkFile, convergenceThreshold)
        pagerank.pagerank()
