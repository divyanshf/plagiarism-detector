import typer
import numpy as np
from nltk import PorterStemmer
import string
from .ProcessorCPP import ProcessorCPP
from .ProcessorJAVA import ProcessorJAVA

ps = PorterStemmer()
puncs = string.punctuation


class FileStructure:
    def __init__(self, filename, document, filetype, path):
        # Basic Features
        self.filename = filename
        self.file = document.read()
        self.filetype = filetype
        self.path = path

        # Strings
        self.stringPos = []

        # Comments
        self.commentsStr = ''
        self.comments = []
        self.commentsPos = []
        self.nComments = 0

        # Variables
        self.variables = []
        self.variablesPos = []
        self.nVariables = 0

        # Functions
        self.functions = []
        self.nFunctions = 0

        # Classes
        self.classes = []
        self.nClasses = 0

    # Tokenize a file
    def tokenize(self, file):
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

    # Check if a value is inside a string in the code
    def checkStringExclusive(self, values, valueIndices, stringPos):
        result = [True for i in range(len(values))]
        for index in range(len(values)):
            valueIndex = valueIndices[index]
            for pos in stringPos:
                start = pos[0]
                end = pos[1]
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

    # Remove the comments from the original file
    def removeComments(self, commentsPos, doc):
        for i in range(len(commentsPos)):
            doc = doc[:(commentsPos[i][0])] + \
                '' + doc[(commentsPos[i][1] + 2):]
            diff = commentsPos[i][1] - commentsPos[i][0] + 2
            for j in range(i+1, len(commentsPos)):
                commentsPos[j] = (commentsPos[j][0] -
                                  diff, commentsPos[j][1] - diff)

        return doc

    # Get the language processor
    def getProcessor(self):
        processor = None
        if self.filetype == '.cpp':
            processor = ProcessorCPP(self.path)
        elif self.filetype == '.java':
            processor = ProcessorJAVA(self.path)
        return processor

    # Extract features
    def extractFeatures(self):
        try:
            processor = self.getProcessor()
            if processor == None:
                text = self.filetype + ' are not supported yet!'
                typer.secho(text, fg=typer.colors.RED)
                raise typer.Exit()

            # Comments Processing
            self.comments, self.commentsPos = processor.extractComments(
                self.file)
            self.nComments = len(self.comments)
            self.file = self.removeComments(self.commentsPos, self.file)

            # # Process strings after removing comments
            self.stringPos = processor.extractStringPositions(self.file)

            # # Variable Processing
            self.variables, self.nVariables = processor.extractVariables(
                self.file, stringPos=self.stringPos)

            # # Functions
            self.functions, self.nFunctions = processor.extractFunctions(
                self.file)

            # # Classes
            self.classes, self.nClasses = processor.extractClasses(self.file)
            return None
        except Exception as ex:
            return str(ex)

    # Process the document
    def processDocument(self):
        err = self.extractFeatures()
        self.file = self.tokenize(self.file)
        self.commentsStr = self.tokenize(''.join(self.comments))
        return err


# Create a feature matrix
def featureMatrix(files):
    result = np.zeros((len(files), 3))
    for index, fs in enumerate(files):
        result[index] = np.array(
            [fs.nVariables, fs.nFunctions, fs.nClasses])
    return result, ['#Variables', '#Functions', '#Classes']
