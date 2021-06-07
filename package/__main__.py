import argparse
import glob
import os
import numpy as np
from colorama.ansi import Back, Fore, Style
from package.OnlineProcessor import OnlineSearch
import pandas as pd
from package.FileProcessor import FileStructure
from package.IREProcessor import IREProcessor
from . import ScreenProcessor as sp


# Initialize colorama
sp.initialize()


# Argument parser
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
    filename = ''
    if primary:
        filename = 'Primary File'
    else:
        _, filename = os.path.split(path)
    print(Fore.LIGHTCYAN_EX + filename +
          Fore.YELLOW + ' : Processing...', end='\r')
    document = open(path, 'r')
    fp = FileStructure(filename, document, pcomment)
    document.close()
    print(Fore.CYAN + filename + Fore.GREEN + ' : Processing Done !')
    return fp


# Get all cpp files from a folder
def pickFolder(pcomment):
    files = []
    while(True):
        # sp.clear()
        try:
            folderPath = input(Style.RESET_ALL +
                               'Path to folder : ' + Fore.BLUE)
            os.chdir(folderPath)
            for file in glob.glob('*.cpp'):
                fp = processDocument(file, pcomment)
                files.append(fp)
            break
        except Exception as ex:
            print(Fore.RED + str(ex))

    return files


# Process corpus
def processCorpus(corpus, filenames, globalForm):
    irp = IREProcessor()

    tdMatrix = irp.createTermDocumentMatrix(corpus)

    tdMatrix = irp.applyWeighting(tdMatrix, globalForm)

    similarity = irp.calculateSimilarity(tdMatrix)
    return similarity


# Display result
def displayResult(dataframe):
    # print(Fore.MAGENTA + '\nReport :' + Style.RESET_ALL)
    # print(dataframe)
    try:
        path = input(Style.RESET_ALL +
                     'Where do you want to save the result : ' + Fore.BLUE)
        lastChar = path[len(path) - 1]
        if lastChar != '/' or lastChar != '\\':
            path = path+'/'
        dataframe.to_csv(path+'result.csv')
        print(Fore.GREEN + 'Saved to ' + Fore.BLUE +
              path + 'result.csv' + Style.RESET_ALL)
    except Exception as ex:
        print(Fore.RED + str(ex))


# Latent Semantic Analysis
def lsaSimilarity(files, pcomment):
    corpusCode = [doc.file for doc in files]
    corpusComment = [doc.comments for doc in files]
    filenames = [doc.filename for doc in files]
    nComments = [doc.nComments for doc in files]

    # Source code without comments
    print(Fore.BLUE + 'Similarity : ' + Fore.YELLOW +
          'Calculating...' + Style.RESET_ALL, end='\r')
    simCode = processCorpus(corpusCode, filenames, 'normal')
    result = simCode[0, :] * 100
    columns = ['Sim(Code)']

    # Comments
    if pcomment:
        simComment = processCorpus(corpusComment, filenames, 'idf')
        result = np.vstack([result, simComment[0, :] * 100])
        columns.append('Sim(Comments)')

    print(Fore.BLUE + 'Similarity : ' + Fore.GREEN +
          'Calculation Done!' + Style.RESET_ALL)

    result = np.vstack([result, nComments])
    columns.append('#Comments')

    result = result.transpose()
    df = pd.DataFrame(result, index=filenames, columns=columns)
    # df.style.highlight_max(subset=['Sim(Code)'])
    df['Sim(Code)'] = df['Sim(Code)'].astype(float).round(2)
    try:
        df['Sim(Comments)'] = df['Sim(Comments)'].astype(float).round(2)
    except:
        None
    df.style.format({'Sim(Code)': ":.2%"})
    return df


# Driver function
def main():
    arguments = parser.parse_args()

    # CLI Version required
    if arguments.version:
        print(Fore.GREEN + 'version=0.1.0' + Style.RESET_ALL)
        if arguments.pcomment == False and arguments.path == None:
            return

    # Clear screen
    sp.clear()

    # If path is not provided in the arguments
    if arguments.path == None:
        path = input('Path to file : ' + Fore.BLUE)

    # Process the documents
    try:
        files = []
        files.append(processDocument(
            arguments.path or path, arguments.pcomment, primary=True))

        # User's choice for checking among files or the internet
        menuChoice = sp.Menu(['Local Similarity', 'Global Similarity'], 0)
        menuChoice.render()
        option = menuChoice.takeInput()
        # option = int(input(Style.RESET_ALL + '\nYour choice : ' + Fore.BLUE))
        if option == 0:
            files = files + pickFolder(arguments.pcomment)
            df = lsaSimilarity(files, arguments.pcomment)
            displayResult(df)
        else:
            print(Fore.BLUE + 'GOOOOOOOOGLE' + Style.RESET_ALL)
            # os = OnlineSearch()
            # os.onlineSearch('Stackoverflow')
    except Exception as ex:
        print(Fore.RED + str(ex))
        return

    # Deinitialize colorama
    sp.deinitialize()


if __name__ == '__main__':
    main()
