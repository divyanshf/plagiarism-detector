import re
from nltk import PorterStemmer
import string

ps = PorterStemmer()
puncs = string.punctuation


class FileProcessor:
    def __init__(self):
        self.file = None
        self.lines = []
        self.comments = []

    def readFile(self, document):
        self.lines = self.file.split('\n')

        # Remove empty strings
        self.lines = list(filter(None, self.lines))

        # Remove leading whitespaces and tabs
        self.lines = list(map(lambda x: x.lstrip(), self.lines))

    # Processing comments assuming the comment characters dont appear inside double quotes or single quotes
    def processComments(self, removeComment):
        patternSingle = re.compile('//.*\n')
        patternMultiple = re.compile('/\*.*\*/', re.DOTALL)

        # Store comments if required
        if removeComment == False:
            self.comments = re.findall(
                patternSingle, self.file) + re.findall(patternMultiple, self.file)

        self.file = re.sub(patternSingle, '\n', self.file)
        self.file = re.sub(patternMultiple, '', self.file)

    # Tokenize the file
    def tokenizeFile(self):
        terms = self.file.split()
        self.file = ''
        for term in terms:
            processedTerms = self.processTerm(term)
            for processedTerm in processedTerms:
                self.file += processedTerm + ' '

    # Split words by  punctuations or digits
    def processTerm(self, word):
        processed = []
        currentTerm = ""

        # Remove punctuations, operators and digits
        for ch in word:
            if ch in puncs or ch.isdigit():
                if currentTerm != "":
                    currentTerm = ps.stem(currentTerm)
                    processed.append(currentTerm)
                currentTerm = ""
            else:
                currentTerm += ch

        if(currentTerm != ""):
            currentTerm = ps.stem(currentTerm)
            processed.append(currentTerm)

        return processed

    # Pre-processinng the file
    def preprocess(self, document, removeComment):
        self.file = document.read()
        self.processComments(removeComment)
        self.readFile(document)
        self.tokenizeFile()
        print(self.file)
