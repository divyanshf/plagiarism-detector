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

    # Processing comments using regex
    # def processCommentsRegex(self, processComment):
    #     comments = []
    #     patternSingle = re.compile('//.*\n')
    #     patternMultiple = re.compile('/\*(.*?)\*/', re.DOTALL)

    #     # Store comments if required
    #     comments = re.findall(
    #         patternSingle, self.file) + re.findall(patternMultiple, self.file)
    #     comments = list(
    #         map(lambda x: x.replace('//', '').replace('/*', '').replace('*/', '').replace('\n', ' ').strip(), comments))
    #     if processComment == True:
    #         # Tokenize comments
    #         self.comments = ' '.join(comments).lower()
    #         self.comments = self.tokenizeFile(self.comments)

    #     # Removing comments from the original file
    #     self.file = re.sub(patternSingle, '\n', self.file)
    #     self.file = re.sub(patternMultiple, '', self.file)
    #     self.nComments = len(comments)

    # Processing comments without using regex
    def processComments(self, processComment):
        comments = []
        commentsIndex = []
        singleComment = -1
        blockComment = -1
        inString = False
        # Parse each character
        for i in range(len(self.file)):
            # Check if a string is running
            if self.file[i] == '\"':
                inString = not(inString)
            # Check if a comment is starting
            if not(inString) and self.file[i] == '/':
                try:
                    if self.file[i+1] == '/':
                        singleComment = i
                    elif self.file[i+1] == '*':
                        blockComment = i
                except:
                    None
            # If the comment is single line comment
            if singleComment != -1:
                if self.file[i] == '\n':
                    comment = self.file[singleComment:i] + '\n'
                    comments.append(comment)
                    commentsIndex.append((singleComment, i-1))
                    singleComment = -1
            # If the comment is a block comment
            if blockComment != -1:
                try:
                    if self.file[i] == '*' and self.file[i+1] == '/':
                        comment = self.file[blockComment:i+1] + '/'
                        comments.append(comment)
                        commentsIndex.append((blockComment, i+1))
                        blockComment = -1
                except:
                    None

        # Remove the comments from the original file
        for i in range(len(commentsIndex)):
            self.file = self.file[:(commentsIndex[i][0] - 1)] + \
                '' + self.file[(commentsIndex[i][1] + 1):]
            diff = commentsIndex[i][1] - commentsIndex[i][0] + 2
            for j in range(i+1, len(commentsIndex)):
                commentsIndex[j] = (commentsIndex[j][0] -
                                    diff, commentsIndex[j][1] - diff)

        # Number of comments
        self.nComments = len(comments)
        # If comments are to be processed
        if processComment:
            # Tokenize comments
            self.comments = ' '.join(comments).lower()
            self.comments = self.tokenizeFile(self.comments)

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
        # self.processComments(processComment)
        # self.readFile(document)
        self.file = self.tokenizeFile(self.file)
