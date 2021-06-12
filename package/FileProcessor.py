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
        self.inString = []
        self.nComments = 0
        self.nVariables = 0
        self.datatypes = ['int', 'char', 'bool',
                          'float', 'double', 'void', 'wchar_t']
        self.datatypeModifier = [
            'signed', 'unsigned', 'short', 'long', 'long long']
        self.preprocess(document, processComment)

    # Read the file and convert it into a list of lines
    # ??? not required ???
    def readFile(self, document):
        self.lines = self.file.split('\n')

        # Remove empty strings
        self.lines = list(filter(None, self.lines))

        # Remove leading whitespaces and tabs
        self.lines = list(map(lambda x: x.lstrip(), self.lines))

    # Find the positions of strings in the code
    def processStrings(self):
        pattern = re.compile('\".*?\"', re.DOTALL)
        self.inString = [(m.start(), m.end() - 1)
                         for m in re.finditer(pattern, self.file)]

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

    # Finding primitive variable declarations using Regex
    # !!! Fix the count of declaration inside a string
    # Doesn't consider the fact that " can be escaped inside the string as well
    def processVariablesRegex(self):
        group = '|'.join(self.datatypeModifier) + \
            '|' + '|'.join(self.datatypes)
        pattern = re.compile(rf'(?:{group})\s.*?;')
        declarations = re.findall(pattern, self.file)
        decPositions = [(m.start(), m.end() - 1)
                        for m in re.finditer(pattern, self.file)]
        declarations, decPositions = self.checkStringExclusive(
            declarations, decPositions)
        for declaration in declarations:
            self.nVariables += declaration.count(',') + 1

    # Check if a value is inside a string in the code
    def checkStringExclusive(self, values, valueIndices):
        result = [True for i in range(len(values))]
        for index in range(len(values)):
            valueIndex = valueIndices[index]
            for stringPos in self.inString:
                start = stringPos[0]
                end = stringPos[1]
                # Completely inside the string
                cond1 = start < valueIndex[0] and end > valueIndex[1]
                # Second half partially inside the string
                cond2 = start < valueIndex[0] and (
                    end < valueIndex[1] and start < valueIndex[1])
                # First half partially inside the string
                cond3 = start > valueIndex[0] and (
                    end > valueIndex[1] and start < valueIndex[1])
                if cond1 or cond2 or cond3:
                    result[index] = False
        values = [value for index, value in enumerate(
            values) if result[index]]
        valueIndices = [valueIndex for index,
                        valueIndex in enumerate(valueIndices) if result[index]]
        return values, valueIndices

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
        self.processStrings()
        # self.processCommentsRegex(processComment)
        # self.readFile(document)
        self.processVariablesRegex()
        self.file = self.tokenizeFile(self.file)
