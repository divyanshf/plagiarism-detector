import os
from typing import Optional
import numpy as np
import typer
import datetime
import pandas as pd
from .Analyser import PathAnalyser, Preference
from .IREProcessor import IREProcessor
from .Processor.FileProcessor import featureMatrix
from .PreferenceModule import app as prefapp


# Global Variables
pref = Preference()
userpref = pref.initialize()


# Typer app
app = typer.Typer(help='Plagiarism Detection in source code files.')
app.add_typer(prefapp, name='preference', help='Customize preferences')


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

    corpusCode = [doc.file for doc in files]
    corpusComment = [doc.commentsStr for doc in files]

    simCode = processCorpus(corpusCode, filenames, 'normal')
    simCode = simCode * 100

    if pcomment:
        commentsWeight = float(userpref['comments_weight'])  # In percentage
        simComment = processCorpus(corpusComment, filenames, 'idf')
        simComment = simComment * 100
        simCode = ((100 - commentsWeight) * simCode +
                   commentsWeight * simComment) / 100

    return simCode


def saveResults(dataframe):
    typer.echo(dataframe)
    timestamp = datetime.datetime.now()
    date = timestamp.strftime("%Y-%m-%d")
    time = timestamp.strftime("%I-%M-%S %p")
    # path = userpref['result_path'] + '\\result'
    path = userpref['result_path'] + '\\' + date
    try:
        if not(os.path.exists(path)):
            os.makedirs(path)
        # os.chmod(path, stat.S_IRWXO)
        path = path + '\\' + time + '.csv'
        dataframe.to_csv(path)
        result = 'Saved to ' + path
        typer.secho(result, fg=typer.colors.GREEN)
    except Exception as ex:
        typer.secho(str(ex), fg=typer.colors.RED)
        raise typer.Exit()


# Represent max two sims
# Can use preference for threshold
def representBinary(sims, files):
    threshold = float(userpref['threshold'])
    simCode = np.triu(sims)
    filenames = [file.filename for file in files]
    bestIndices = np.argwhere(simCode >= threshold)
    bestIndices = list(filter(lambda x: x[0] != x[1], bestIndices))
    result = np.zeros(len(bestIndices))
    columns = []
    for index, value in enumerate(bestIndices):
        col = filenames[value[0]] + ' and ' + filenames[value[1]]
        columns.append(col)
        result[index] = simCode[value[0]][value[1]]
    if len(bestIndices) > 0:
        df = pd.DataFrame(result.transpose(), index=columns,
                          columns=['Similarity'])
        df = df.sort_values(by=['Similarity'], ascending=False)
        saveResults(df)
    else:
        typer.secho('NO PLAGIARISM ABOVE THRESHOLD FOUND.',
                    fg=typer.colors.GREEN)


# Represent multiple file sims
def representPrimary(simCode, files):
    threshold = float(userpref['threshold'])
    filenames = [file.filename for file in files]
    filenames[0] = 'PRIMARY'
    columns = []
    simCode = simCode[0, :]
    bestIndices = np.argwhere(simCode >= threshold)
    result = np.zeros(len(bestIndices))
    for index, value in enumerate(bestIndices):
        result[index] = simCode[value[0]]
        columns.append(filenames[value[0]])
    df = pd.DataFrame(result, columns=['Similarity'], index=[columns])
    df = df.sort_values(by=['Similarity'], ascending=False)
    saveResults(df)


# Detect similarity
# SINGLE PATH : FOLDER
# TWO PATHS : (TWO FILES) or (ONE FILE and ONE FOLDER)
@app.command(help='Compare source code files for similarity.')
def compare(path1: str = typer.Argument(..., help='Path to a file or folder'), path2: str = typer.Argument('', help='Path to a file or folder'), filetype: str = typer.Option(userpref['filetype'], help='The extension of the files to be processed'), pcomment: bool = typer.Option(False, help='Process comments for similarity')):
    # Remove leading period sign from the filetype
    filetype = filetype.lstrip('.')

    analyser = PathAnalyser(filetype)

    rep = 'b'
    # Check for single path
    if path2 == '':
        isDir, error = analyser.isDir(path1)
        if isDir:
            files = analyser.processPath(path1)
            typer.secho('Processing files ...', fg=typer.colors.YELLOW)
            for file in files:
                file.processDocument()
        else:
            text = path1 + ' : ' + error
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()
    # Check for both paths
    else:
        filetype, error = analyser.setExtension(path1)
        if filetype:
            files = analyser.processPath(path1) + analyser.processPath(path2)
            typer.secho('Processing files ...', fg=typer.colors.YELLOW)
            for file in files:
                file.processDocument()
            isDir2, error = analyser.isDir(path2)
            if isDir2:
                rep = 'p'
        else:
            text = path1 + ' : ' + error
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()

    # Two ways to represent
    # (FOLDER) and (FILE-FILE)  => BINARY
    # (FILE-FOLDER)  => DATAFRAME
    if len(files) != 0:
        result = calculateSimilarity(files, pcomment)
        # representBinary(result, files)
        if rep == 'b':
            representBinary(result, files)
        else:
            representPrimary(result, files)
    else:
        text = 'No .' + filetype + ' files found!'
        typer.secho(text, fg=typer.colors.RED)


# Extract features of the code
# THE PATH MUST LEAD TO A FILE ONLY!
@app.command(help='Extract features from source code files.')
def extract(path: str = typer.Argument(..., help='Path to the file or folder')):
    analyser = PathAnalyser()
    filetype, error = analyser.setExtension(path)
    if filetype:
        fs = (analyser.processPath(path))[0]
        fs.extractFeatures()
        result, features = featureMatrix([fs])
        df = pd.DataFrame(result, columns=[features], index=[fs.filename])
        typer.echo(df)
    else:
        isDir, errDir = analyser.isDir(path)
        if isDir:
            files = analyser.processPath(path)
            for file in files:
                file.extractFeatures()
            if len(files) != 0:
                result, features = featureMatrix(files)
                df = pd.DataFrame(
                    result, columns=[features], index=[fs.filename for fs in files])
                typer.echo(df)
            else:
                typer.secho('No files found!', fg=typer.colors.RED)
                raise typer.Exit()
        else:
            text = path + ' : Invalid Path!'
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()


# Display the version
def versionCallback(value: bool):
    if value:
        typer.echo('version=1.0')
        raise typer.Exit()


# The main callback
@ app.callback()
def main(version: Optional[bool] = typer.Option(None, "--version", callback=versionCallback, is_eager=True, help="Displays the version of Plag.")):
    None


def start():
    app()


if __name__ == '__main__':
    start()
