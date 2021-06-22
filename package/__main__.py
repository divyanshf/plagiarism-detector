from typing import Optional
import numpy as np
import typer
from .Analyser import PathAnalyser, Preference
from .IREProcessor import IREProcessor
from .Processor.FileProcessor import featureMatrix
import pandas as pd


# Global Variables
pref = Preference()
userpref = pref.initialize()


# Typer app
app = typer.Typer(help='Plagiarism Detection in source code files.')


# Process corpus
def processCorpus(corpus, filenames, globalForm):
    irp = IREProcessor()

    tdMatrix = irp.createTermDocumentMatrix(corpus)

    tdMatrix = irp.applyWeighting(tdMatrix, globalForm)

    similarity = irp.calculateSimilarity(tdMatrix)
    return similarity


# Calculate similarity
def calculateSimilarity(files, pcomment):
    filenames = [doc.filename for doc in files]
    nComments = [doc.nComments for doc in files]
    nVariables = [doc.nVariables for doc in files]
    columns = []

    corpusCode = [doc.file for doc in files]
    corpusComment = [doc.commentsStr for doc in files]
    # typer.echo(corpusComment)

    simCode = processCorpus(corpusCode, filenames, 'normal')
    result = simCode[0, :] * 100
    columns.append('Sim(Code)')

    if pcomment:
        simComment = processCorpus(corpusComment, filenames, 'idf')
        result = np.vstack([result, simComment[0, :] * 100])
        columns.append('Sim(Comments)')

    result = np.vstack([result, nComments])
    columns.append('#Comments')

    result = np.vstack([result, nVariables])
    columns.append('#Variables')

    return result, columns


# Detect similarity
# SINGLE PATH : FOLDER
# TWO PATHS : TWO FILES OR ONE FILE - ONE FOLDER
@app.command(help='Compare source code files for similarity.')
def compare(path1: str = typer.Argument(..., help='Path to a file or folder'), path2: str = typer.Argument('', help='Path to a file or folder'), filetype: str = typer.Option(userpref['filetype'], help='The extension of the files to be processed'), pcomment: bool = typer.Option(False, help='Process comments for similarity')):
    # Remove leading period sign from the filetype
    typer.echo(filetype)
    filetype = filetype.lstrip('.')

    analyser = PathAnalyser(filetype)

    # Check for single path
    if path2 == '':
        isDir, error = analyser.isDir(path1)
        if isDir:
            files = analyser.processPath(path1)
            for file in files:
                file.processDocument()
        else:
            text = path1 + ' : ' + error
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()
    # Check for both paths
    else:
        isFile1, error = analyser.isFile(path1)
        if isFile1:
            files = analyser.processPath(path1) + analyser.processPath(path2)
            for file in files:
                file.processDocument()
        else:
            text = path1 + ' : ' + error
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()

    result, columns = calculateSimilarity(files, pcomment)
    df = pd.DataFrame(result.transpose(), columns=columns)
    typer.echo(df)


# Extract features of the code
# THE PATH MUST LEAD TO A FILE ONLY!
@app.command(help='Extract features from source code files.')
def extract(path: str = typer.Argument(..., help='Path to the file')):
    analyser = PathAnalyser()
    filetype, error = analyser.setExtension(path)
    if filetype:
        fs = (analyser.processPath(path))[0]
        fs.extractFeatures()
        result, features = featureMatrix(fs)
        df = pd.DataFrame(result, columns=[fs.filename], index=[features])
        typer.echo(df)
    else:
        text = path + ' : ' + error
        typer.secho(text, fg=typer.colors.RED)
        raise typer.Exit()


# Set preferences
@app.command(help='Set user preference as required.')
def setpref(key: str = typer.Argument(..., help='Specify the key of the preference'), value: str = typer.Argument(..., help='Specify the value of the preference')):
    global userpref
    pref = Preference()
    if pref.check(key):
        userpref[key] = value
        pref.createPreferences(pref.getPreferencePath(), userpref)
        typer.secho('Preferences set!', fg=typer.colors.GREEN)
    else:
        typer.secho('Invalid preference key!', fg=typer.colors.RED)
        raise typer.Exit()


# Reset preferences
@app.command(help='Reset all the preferences to default values.')
def resetpref():
    pref = Preference()
    pref.resetPreferences(pref.getPreferencePath())
    typer.secho('Preferences set to default!', fg=typer.colors.GREEN)


# Display the version
def versionCallback(value: bool):
    if value:
        typer.echo('version=0.1')
        raise typer.Exit()


# The main callback
@ app.callback()
def main(version: Optional[bool] = typer.Option(None, "--version", callback=versionCallback, is_eager=True, help="Displays the version of Plag.")):
    None


def start():
    app()


if __name__ == '__main__':
    start()
