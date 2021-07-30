import re
import plyj.parser as plyj
import plyj.model as model


# Java File Processor
class ProcessorJAVA:
    def __init__(self, path):
        self.stringPattern = re.compile('\".*?\"', re.DOTALL)
        self.singleCommentPattern = re.compile('//.*\n')
        self.blockCommentPattern = re.compile('/\*(.*?)\*/', re.DOTALL)
        self.parser = plyj.Parser()
        self.tree = self.parser.parse_file(path)

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
    def extractVariables(self, doc, stringPos=[]):
        declarations = []
        vDeclarators = []
        typeDeclarations = self.tree.type_declarations
        for decl in typeDeclarations:
            bodyDeclarations = decl.body
            for bDecl in bodyDeclarations:
                if (type(bDecl) == model.FieldDeclaration):
                    vDeclarators += bDecl.variable_declarators
                elif (type(bDecl) == model.MethodDeclaration):
                    mDeclBody = bDecl.body
                    for vDecl in mDeclBody:
                        if(type(vDecl) == model.VariableDeclaration):
                            vDeclarators += vDecl.variable_declarators

        for decl in vDeclarators:
            declarations.append(decl.variable.name)

        return declarations, len(declarations)

    # Extract functions
    def extractFunctions(self, file):
        functions = []
        typeDeclarations = self.tree.type_declarations
        for decl in typeDeclarations:
            bodyDeclarations = decl.body
            for bDecl in bodyDeclarations:
                if(type(bDecl) == model.MethodDeclaration):
                    functions.append(decl.name)
        return functions, len(functions)

    # Extract classes
    def extractClasses(self, file):
        classes = []
        typeDeclarations = self.tree.type_declarations
        for decl in typeDeclarations:
            if(type(decl) == model.ClassDeclaration):
                classes.append(decl.name)
        return classes, len(classes)
