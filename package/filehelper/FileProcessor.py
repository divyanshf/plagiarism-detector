import re


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

    # Pre-processinng the file
    def preprocess(self, document, removeComment):
        self.file = document.read()
        self.processComments(removeComment)
        self.readFile(document)
