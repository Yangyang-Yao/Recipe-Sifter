#!/usr/bin/python3

import sys, os
from porterStemmer import PorterStemmer


class Preprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()

        # list of non-words
        self. nonwords = {'', ' ', '.', ',', "'", "'s", '...'}

        self.stopwords = set()
        with open('stopwords', 'r') as fopen:
            for word in fopen:
                self.stopwords.add(word.strip().lower())


    def stemTokens(self, tokens):
        stemmedTokens = [ self.stemmer.stem(token, 0, len(token) - 1) for token in tokens ]
        return stemmedTokens


    def tokenizeText(self, text):
        """splits text into a list of tokens."""

        # split text by white space
        rawTokens = text.split()
        tokens = []
        for token in rawTokens:
            # skip empty tokens
            if token.isspace() or token.isnumeric():
                continue

            processedToken = token.lower()
            
            if not processedToken[0].isalnum():
                processedToken = processedToken[1:]

            while processedToken and not processedToken[-1].isalnum():
                processedToken = processedToken[:-1]
            
            if processedToken and processedToken not in self.nonwords and processedToken not in self.stopwords:
                tokens.append(processedToken)
        
        return tokens


    def preprocess(self, input):
        tokens = self.tokenizeText(input)
        stemmedTokens = self.stemTokens(tokens)

        return stemmedTokens


def main(inputDir):
    """iterates through input directory and processes data."""
    preprocessor = Preprocessor()
    tokenList = []
    with os.scandir(inputDir) as dir:
        for file in dir:
            tokens = preprocessor.preprocess(file)
            tokenList.extend(tokens)
    
    preprocessor.processWords(tokenList)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: preprocess.py <input-folder>')
    else:
        input = sys.argv[1]
        main(input)
