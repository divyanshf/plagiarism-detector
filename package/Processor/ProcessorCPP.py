import re
import CppHeaderParser as parser

cppDatatypes = ['int', 'char', 'bool',
                'float', 'double', 'void', 'wchar_t']
cppDatatypeModifier = [
    'signed', 'unsigned', 'short', 'long', 'long long']
cppVariableGroup = '|'.join(cppDatatypeModifier) + \
    '|' + '|'.join(cppDatatypes)


# C++ File Processor
class ProcessorCPP:
    def __init__(self, path):
        self.stringPattern = re.compile('\".*?\"', re.DOTALL)
        self.singleCommentPattern = re.compile('//.*\n')
        self.blockCommentPattern = re.compile('/\*(.*?)\*/', re.DOTALL)
        self.variablePattern = re.compile(rf'(?:{cppVariableGroup})\s.*?;')
        self.parser = parser.CppHeader(path)

    # Return the position of strings present in the document
    # Doesnt consider escaped \" inside a string like string = "something \" ."
    def extractStringPositions(self, doc):
        stringPos = [(m.start(), m.end() - 1)
                     for m in re.finditer(self.stringPattern, doc)]

        return stringPos

    # Regex to find comments in the code
    def extractComments(self, doc):
        comments = []
        commentsPos = []
        singleComment = -1
        blockComment = -1
        inString = False
        # Parse each character
        for i in range(len(doc)):
            # Check if a string is running
            if doc[i] == '\"':
                inString = not(inString)
            # Check if a comment is starting
            if not(inString) and doc[i] == '/':
                try:
                    if doc[i+1] == '/':
                        singleComment = i
                    elif doc[i+1] == '*':
                        blockComment = i
                except:
                    None
            # If the comment is single line comment
            if singleComment != -1:
                if doc[i] == '\n':
                    comment = doc[singleComment:i] + '\n'
                    comments.append(comment)
                    commentsPos.append((singleComment, i-1))
                    singleComment = -1
            # If the comment is a block comment
            if blockComment != -1:
                try:
                    if doc[i] == '*' and doc[i+1] == '/':
                        comment = doc[blockComment:i+1] + '/'
                        comments.append(comment)
                        commentsPos.append((blockComment, i+1))
                        blockComment = -1
                except:
                    None

        return comments, commentsPos

    # Regex to find variables in the code
    def extractVariables(self, doc, stringPos):
        declarations = re.findall(self.variablePattern, doc)
        declarationsPos = [(m.start(), m.end() - 1)
                           for m in re.finditer(self.variablePattern, doc)]

        declarations, declarationsPos = self.checkStringExclusive(
            declarations, declarationsPos, stringPos)

        declarations, declarationsPos = self.checkVariableDeclarations(
            declarations, declarationsPos)

        nDeclarations = self.countVariables(declarations)

        return declarations, nDeclarations

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

    # Check variable declaration for function definitons
    def checkVariableDeclarations(self, declarations, declarationsPos):
        result = [True if(self.checkFuncDeclaration(
            cppVariableGroup, dec)) else False for dec in declarations]
        declarations = [dec for ind, dec in enumerate(
            declarations) if not(result[ind])]
        declarationsPos = [pos for ind, pos in enumerate(
            declarationsPos) if not(result[ind])]

        return declarations, declarationsPos

    # Count the number of variables in the declaration
    def countVariables(self, declarations):
        nVariables = 0
        for declaration in declarations:
            stack = []
            for char in declaration:
                if (char == '(' or char == ')'):
                    invChar = '(' if char == ')' else ')'
                    if len(stack) != 0 and stack[-1] == invChar:
                        stack.pop()
                    else:
                        stack.append(char)
                elif (char == ',' or char == ';') and len(stack) == 0:
                    nVariables += 1
        return nVariables

    # Extract functions
    def extractFunctions(self, file):
        functions = [f['name'] for f in self.parser.functions]
        return functions, len(functions)

    # Extract classes
    def extractClasses(self, file):
        classes = [c for c in self.parser.classes]
        return classes, len(classes)

    # Check if the declaration is of a variable or a function
    # int sum(int a, int b) || int sum(0)
    def checkFuncDeclaration(self, group, declaration):
        result = False
        try:
            pattern = re.compile(rf'\((?:{group})\s.*?\)')
            par = re.findall(pattern, declaration)
            if par:
                result = True
        except:
            None
        return result
