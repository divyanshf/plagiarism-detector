import argparse
import glob
import os
import pandas as pd
from filehelper.FileProcessor import FileStructure
from irehelper.IREProcessor import IREProcessor

parser = argparse.ArgumentParser()

# Add custom arguments to the the parser
parser.add_argument('--version', '-v',
                    help='Display the version of the application.', action='store_true')
parser.add_argument('--pcomment', '-pc',
                    help='Process the comments during pre-processing.', action='store_true')
parser.add_argument(
    '--path', '-p', help='The path of the file you want to check.')


# Initialize
def processDocument(path, pcomment, primary=False):
    document = open(path, 'r')
    filename = ''
    if primary:
        filename = 'Primary File'
    else:
        _, filename = os.path.split(path)
    fp = FileStructure(filename, document, pcomment)
    document.close()
    return fp


# Get all cpp files from a folder
def pickFolder(pcomment):
    folderPath = input('Path to folder : ')
    files = []
    try:
        os.chdir(folderPath)
        for file in glob.glob('*.cpp'):
            fp = processDocument(file, pcomment)
            files.append(fp)
    except Exception as ex:
        print(ex)

    return files


# Latent Semantic Analysis
def lsaSimilarity(files, pcomment):
    irp = IREProcessor(pcomment)
    corpusCode = [doc.file for doc in files]
    # tdMatrixCode = irp.createVectorizerImplementation(corpusCode)
    tdMatrixCode = irp.createTermDocumentMatrix(corpusCode)
    tdMatrixCode = irp.applyTNCWeighting(tdMatrixCode)
    similarity = irp.calculateSimilarity(tdMatrixCode)


# Driver function
def main():
    arguments = parser.parse_args()

    # CLI Version required
    if arguments.version:
        print('version=0.1.0')
        if arguments.pcomment == False and arguments.path == None:
            return

    # If path is not provided in the arguments
    if arguments.path == None:
        path = input('Path to file : ')

    # Process the documents
    try:
        files = []
        files.append(processDocument(
            arguments.path or path, arguments.pcomment, primary=True))

        # User's choice for checking among files or the internet
        option = int(input('Your choice : '))
        if option == 1:
            files = files + pickFolder(arguments.pcomment)
            lsaSimilarity(files, arguments.pcomment)
        else:
            print('GOOOOOOOGLE')
    except Exception as ex:
        print(ex)
        return


if __name__ == '__main__':
    main()
