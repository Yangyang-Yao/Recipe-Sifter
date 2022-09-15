#!/usr/bin/python3

import sys, queue, requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib import parse, robotparser
from preprocess import Preprocessor
from common import Doc, Word


class Crawler:
    def __init__(self, seedFile, maxUrls):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        self.maxUrls = maxUrls
        self.preprocessor = Preprocessor()
        self.robotparser = robotparser.RobotFileParser()
        self.frontier = queue.Queue()
        self.crawledUrls = set()
        self.validDomains = set()
        self.disallowed = set()
        self.index = defaultdict(Word)
        self.docs = []
        self.numWords = 0
        self.numDocs = 0
        self.initialize(seedFile)
        for d in self.validDomains:
            print(d)


    def initialize(self, seedFile):
        with open(seedFile, 'r') as fopen:
            for line in fopen:
                url = line.strip()

                # add to frontier
                self.frontier.put(self.normalizeUrl(url))

                # add to valid domains (both with and without www.)
                hostname = parse.urlparse(url).hostname
                self.validDomains.add(hostname)
                self.validDomains.add(hostname.split('.', 1)[1])

                # parse robots.txt
                self.parseRobots(url)


    def parseRobots(self, url):
        parsedUrl = parse.urlparse(url)
        topLevelUrl = f'{parsedUrl.scheme}://{parsedUrl.hostname}'
        robotsUrl = f'{topLevelUrl}/robots.txt'
        try:
            response = requests.get(robotsUrl, headers=self.headers, timeout=1)
        except:
            return

        html = response.text
        start = html.find('User-agent: *')
        if start == -1:
            return
        
        lines = html[start:].split('\n')[1:]
        for line in lines:
            if 'User-agent' in line:
                break

            splitted = line.split(' ')
            if len(splitted) != 2:
                continue
            if splitted[0] != 'Disallow:':
                continue

            disallowedUrl = topLevelUrl + splitted[1].strip()
            if disallowedUrl[-1] == '*':
                disallowedUrl = disallowedUrl[:-1]
            self.disallowed.add(disallowedUrl)
    

    def normalizeUrl(self, url):
        return url[:-1] if url[-1] == '/' else url
    

    def isValid(self, url):
        # relative link, so valid
        if 'http' not in url:
            return True

        parsedUrl = parse.urlparse(url)
        if parsedUrl.hostname not in self.validDomains:
            return False
        
        return True
    

    def getUrlFromRelative(self, url, relative):
        # if relative doesn't start with "/",
        # build off current URL
        if relative[0] != '/':
            return self.normalizeUrl(url + '/' + relative)
        
        # else, build off top-level URL
        splittedUrl = url.split('/')
        relativeUrl = ''
        for i in range(3):
            relativeUrl += splittedUrl[i] + '/'
        
        return self.normalizeUrl(relativeUrl + relative[1:])


    def processDoc(self, url, text):
        words = self.preprocessor.preprocess(text)
        wordSet = set()
        docLength = 0

        for word in words:
            if word not in wordSet:
                self.index[word].numDocs += 1
                wordSet.add(word)
            
            self.index[word].positions.append(self.numWords)
            self.numWords += 1
            docLength += 1

        self.docs.append(Doc(url, docLength))

    
    def writeFiles(self):
        with open('index.txt', 'w') as fout:
            for word, wordData in self.index.items():
                fout.write(f'{word} {wordData.numDocs} ')
                for pos in wordData.positions:
                    fout.write(f'{pos} ')
                fout.write('\n')
        
        with open('docs.txt', 'w') as fout:
            for i, doc in enumerate(self.docs):
                fout.write(f'{i} {doc.url} {doc.length}\n')


    # DEBUGGING
    def printIndex(self):
        for word, wordData in self.index.items():
            print(f'{word}: {wordData.numDocs} ', end='')
            for pos in wordData.positions:
                print(f'{pos} ', end='')
            print()
    

    def allowed(self, url):
        splitted = url.split('/')
        partialUrl = ''
        for elem in splitted:
            partialUrl += elem + '/'
            if partialUrl in self.disallowed:
                return False
        
        return True


    def crawl(self):
        crawlerOutput = open('crawler.output', 'w')
        linksOutput = open('links.output', 'w') 

        while len(self.crawledUrls) < self.maxUrls:
            # get next URL to crawl, making sure we have not
            # crawled it already
            currUrl = self.frontier.get()
            while currUrl in self.crawledUrls:
                currUrl = self.frontier.get()

            # do not crawl if disallowed by robots.txt
            if not self.allowed(currUrl):
                continue

            # crawl this URL
            try:
                response = requests.get(currUrl, headers=self.headers, timeout=1)
            except:
                continue
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # if title empty just skip it
            if not soup.title:
                continue

            if not soup.title.string:
                continue

            # DEBUG
            print(f'{len(self.crawledUrls)} {currUrl}')

            # add current URL to crawled URLs
            self.crawledUrls.add(currUrl)

            # add current URL to crawler.output
            crawlerOutput.write(currUrl + '\n')

            # to avoid duplicate urls
            links = set()
            
            # extract all links
            for link in soup.find_all('a'):
                rawUrl = link.get('href')

                # skip:
                #  - empty links
                #  - links that are only a "/"
                #  - links with spaces
                #  - links with "#" in them
                #  - links with "javascript" in them
                if not rawUrl or rawUrl == '/' or ' ' in rawUrl or '#' in rawUrl or 'javascript' in rawUrl:
                    continue

                url = self.normalizeUrl(rawUrl)

                # handle irregular links
                if 'http' not in url:
                    if 'www.' in url:
                        url = 'https://' + url
                    else:
                        url = self.getUrlFromRelative(currUrl, url)

                # only add URLs in valid domains
                if self.isValid(url):
                    links.add(url)

            for link in links:
                # output to links.output
                linksOutput.write(currUrl + ' ' + link + '\n')

                # only add URLs to frontier that we
                # have not already crawled
                if link not in self.crawledUrls:
                    self.frontier.put(link)

            title = soup.title.string
            self.processDoc(currUrl, title)
    
        crawlerOutput.close()
        linksOutput.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: crawler.py <seed-file> <max-number-URLs>')
    else:
        seedFile = sys.argv[1]
        maxUrls = int(sys.argv[2])
        crawler = Crawler(seedFile, maxUrls)
        crawler.crawl()
        crawler.printIndex()
        crawler.writeFiles()
