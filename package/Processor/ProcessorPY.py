import re
import ast

import typer


# Python File Processor
class ProcessorPY:
    def __init__(self, path):
        self.stringPatternSingle = re.compile('\'.*?\'', re.DOTALL)
        self.stringPatternDouble = re.compile('\".*?\"', re.DOTALL)
        self.commentPattern = re.compile('#.*\n')
        self.path = path
        self.code = open(path).read()
        self.tree = ast.parse(self.code)

    # Return the position of strings present in the document
    # Doesnt consider escaped \" inside a string like string = "something \" ."
    def extractStringPositions(self, doc):
        stringPos = [(m.start(), m.end() - 1)
                     for m in re.finditer(self.stringPatternDouble, doc)] + [(m.start(), m.end() - 1)
                                                                             for m in re.finditer(self.stringPatternSingle, doc)]

        return stringPos

    # Regex to find comments in the code
    def extractComments(self, doc):
        comments = [m for m in re.findall(self.commentPattern, doc)]
        commentsPos = [(m.start(), m.end() - 1)
                       for m in re.finditer(self.commentPattern, doc)]

        return comments, commentsPos

    # Regex to find variables in the code
    def extractVariables(self, doc, stringPos=[]):
        declarations = []

        body = self.tree.body
        for bodyContent in body:
            if type(bodyContent) == ast.Assign:
                targets = bodyContent.targets
                declarations += [t.id for t in targets]
            elif type(bodyContent) == ast.FunctionDef:
                funcBody = bodyContent.body
                for funcContent in funcBody:
                    if type(funcContent) == ast.Assign:
                        targets = funcContent.targets
                        declarations += [
                            t.id for t in targets if type(t) == ast.Name]
            elif type(bodyContent) == ast.For:
                forBody = bodyContent.body
                for forContent in forBody:
                    if type(forContent) == ast.Assign:
                        targets = forContent.targets
                        declarations += [
                            t.id for t in targets if type(t) == ast.Name]

        return declarations, len(declarations)

    # Extract functions
    def extractFunctions(self, file):
        functions = []

        body = self.tree.body
        for bodyContent in body:
            if type(bodyContent) == ast.FunctionDef:
                functions.append(bodyContent.name)

        return functions, len(functions)

    # Extract classes
    def extractClasses(self, file):
        classes = []

        body = self.tree.body
        for bodyContent in body:
            if type(bodyContent) == ast.ClassDef:
                classes.append(bodyContent.name)

        return classes, len(classes)
