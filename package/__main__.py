import os
from typing import Optional
import numpy as np
import typer
import pandas as pd
from .ScreenProcessor.ScreenProcessor import ScreenProcessor
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


# Screen Processor
sp = ScreenProcessor(userpref=userpref)


# Process corpus
def processCorpus(corpus, globalForm):
    irp = IREProcessor()

    tdMatrix = irp.createTermDocumentMatrix(corpus)
    tdMatrix = irp.applyWeighting(tdMatrix, globalForm)
    similarity = irp.calculateSimilarity(tdMatrix)

    return similarity


# Process features
def processFeatures(corpus):
    irp = IREProcessor()
    featMatrix, _ = featureMatrix(corpus)
    simFeatures = irp.calculateSimilarity(featMatrix)

    return simFeatures


# Calculate similarity
def calculateSimilarity(files, pcomment):
    filenames = [doc.filename for doc in files]

    corpusCode = [doc.file for doc in files]
    corpusComment = [doc.commentsStr for doc in files]

    initial = sp.printProcessInitial('Calculating textual similarity...')
    simCode = processCorpus(corpusCode, 'normal')
    simCode = simCode * 100
    sp.printProcessFinal(initial, 'Textual similarity calculated!')

    if pcomment:
        initial = sp.printProcessInitial('Calculating comments similarity...')
        commentsWeight = float(userpref['comment_weight'])  # In percentage
        simComment = processCorpus(corpusComment, 'idf')
        simComment = simComment * 100
        simCode = ((100 - commentsWeight) * simCode +
                   commentsWeight * simComment) / 100
        sp.printProcessFinal(initial, 'Comments Similarity calculated!')

    initial = sp.printProcessInitial('Calculating feature-based similarity...')
    simFeatures = processFeatures(files) * 100
    simCode = (simCode + simFeatures) / 2
    sp.printProcessFinal(initial, 'Feature-based Similarity calculated!')

    return simCode


# Detect similarity
# SINGLE PATH : FOLDER
# TWO PATHS : (TWO FILES) or (ONE FILE and ONE FOLDER)
@app.command(help='Compare source code files for similarity.')
def compare(path1: str = typer.Argument(..., help='Path to a file or folder'), path2: str = typer.Argument('', help='Path to a file or folder'), filetype: str = typer.Option(userpref['filetype'], help='The extension of the files to be processed'), pcomment: bool = typer.Option(False, help='Process comments for similarity')):
    # Remove leading period sign from the filetype
    filetype = filetype.lstrip('.')

    analyser = PathAnalyser(filetype)
    userpref['filetype'] = filetype

    rep = 'b'
    # Check for single path
    if path2 == '':
        isDir, error = analyser.isDir(path1)
        if isDir:
            files = analyser.processPath(path1)
            # Notify user
            if len(files) > 0:
                initial = sp.printProcessInitial('Processing files...')
            # Process features
            for file in files:
                file.processDocument()
            # Notify user
            if len(files) > 0:
                sp.printProcessFinal(initial, 'Files Processed!')
        else:
            text = path1 + ' : ' + error
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()
    # Check for both paths
    else:
        filetype, error = analyser.setExtension(path1)
        if filetype:
            files = analyser.processPath(path1) + analyser.processPath(path2)
            # Notify user
            if len(files) > 0:
                initial = sp.printProcessInitial('Processing files...')
            # Process features
            for file in files:
                file.processDocument()
            # Notify user
            if len(files) > 0:
                sp.printProcessFinal(initial, 'Files Processed!')
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
        if rep == 'b':
            sp.representBinary(result, files, [path1, path2])
        else:
            sp.representPrimary(result, files, [path1, path2])
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
            # Notify user
            if len(files) > 0:
                initial = sp.printProcessInitial('Processing files...')
            for file in files:
                # Extract features
                file.extractFeatures()
            if len(files) != 0:
                # Notify user
                sp.printProcessFinal(initial, 'Files Processed!')

                # Get feature matrix
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
