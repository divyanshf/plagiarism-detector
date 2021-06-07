import re
from nltk import PorterStemmer
import string

ps = PorterStemmer()
puncs = string.punctuation


class FileStructure:
    def __init__(self, name, document, processComment):
        self.filename = name
        self.file = None
        self.lines = []
        self.comments = ''
        self.nComments = 0
        self.preprocess(document, processComment)

    # Read the file and convert it into a list of lines
    # ??? not required ???
    def readFile(self, document):
        self.lines = self.file.split('\n')

        # Remove empty strings
        self.lines = list(filter(None, self.lines))

        # Remove leading whitespaces and tabs
        self.lines = list(map(lambda x: x.lstrip(), self.lines))

    # Processing comments assuming the comment characters dont appear inside double quotes or single quotes
    def processComments(self, processComment):
        comments = []
        patternSingle = re.compile('//.*\n')
        patternMultiple = re.compile('/\*(.*?)\*/', re.DOTALL)

        # Store comments if required
        comments = re.findall(
            patternSingle, self.file) + re.findall(patternMultiple, self.file)
        comments = list(
            map(lambda x: x.replace('//', '').replace('/*', '').replace('*/', '').replace('\n', ' ').strip(), comments))
        if processComment == True:
            # Tokenize comments
            self.comments = ' '.join(comments).lower()
            self.comments = self.tokenizeFile(self.comments)

        # Removing comments from the original file
        self.file = re.sub(patternSingle, '\n', self.file)
        self.file = re.sub(patternMultiple, '', self.file)
        self.nComments = len(comments)

    # Tokenize the file
    def tokenizeFile(self, file):
        terms = file.split()
        file = ''
        for term in terms:
            processedTerms = self.processTerm(term)
            for processedTerm in processedTerms:
                file += processedTerm + ' '

        return file

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
    def preprocess(self, document, processComment):
        self.file = document.read()
        self.processComments(processComment)
        # self.readFile(document)
        self.file = self.tokenizeFile(self.file)
