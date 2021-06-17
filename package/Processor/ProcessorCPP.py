import re


cppDatatypes = ['int', 'char', 'bool',
                'float', 'double', 'void', 'wchar_t']
cppDatatypeModifier = [
    'signed', 'unsigned', 'short', 'long', 'long long']
cppVariableGroup = '|'.join(cppDatatypeModifier) + \
    '|' + '|'.join(cppDatatypes)


# C++ File Processor
class ProcessorCPP:
    def __init__(self):
        self.stringPattern = re.compile('\".*?\"', re.DOTALL)
        self.singleCommentPattern = re.compile('//.*\n')
        self.blockCommentPattern = re.compile('/\*(.*?)\*/', re.DOTALL)
        self.variablePattern = re.compile(rf'(?:{cppVariableGroup})\s.*?;')

    # Return the position of strings present in the document
    # Doesnt consider escaped \" inside a string like string = "something \" ."
    def extractStringPositions(self, doc):
        stringPos = [(m.start(), m.end() - 1)
                     for m in re.finditer(self.stringPattern, doc)]

        return stringPos

    # Regex to find comments in the code
    def extractComments(self, doc):
        comments = re.findall(self.singleCommentPattern, doc) + \
            re.findall(self.blockCommentPattern, doc)
        commentsPos = [(m.start(), m.end() - 1) for m in re.finditer(self.singleCommentPattern, doc)] + [
            (m.start(), m.end() - 1) for m in re.finditer(self.blockCommentPattern, doc)]

        return comments, commentsPos

    # Regex to find variables in the code
    def extractVariables(self, doc):
        nVariables = 0
        declarations = re.findall(self.variablePattern, doc)
        declarationsPos = [(m.start(), m.end() - 1)
                           for m in re.finditer(self.variablePattern, doc)]

        declarations = [dec for dec in declarations if not(
            self.checkFuncDeclaration(cppVariableGroup, dec))]
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

        return declarations, declarationsPos, nVariables

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
