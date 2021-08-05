import typer
from typing import Optional
import pandas as pd
import numpy as np
from .ScreenProcessor.ScreenProcessor import ScreenProcessor
from .Analysers.PathAnalyser import PathAnalyser
from .Analysers.PreferenceAnalyser import Preference
from .Comparator.IREProcessor import IREProcessor
from .Processor.FileProcessor import featureMatrix
from .AppModule.PreferenceModule import app as prefapp


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
    irp = IREProcessor()
    filenames = [doc.filename for doc in files]

    corpusCode = [doc.file for doc in files]
    corpusComment = [doc.commentsStr for doc in files]

    initial = sp.printProcessInitial('Calculating similarity...')
    codeMatrix = irp.createTermDocumentMatrix(corpusCode)
    codeMatrix = irp.applyWeighting(codeMatrix, 'normal')
    simCode = irp.calculateSimilarity(codeMatrix)

    if pcomment:
        commentsWeight = float(userpref['comment_weight'])  # In percentage
        commentMatrix = irp.createTermDocumentMatrix(corpusComment)
        commentMatrix = irp.applyWeighting(commentMatrix, 'idf')
        simComments = irp.calculateSimilarityByEuclideanMethod(
            commentMatrix, sigma=0.3)
        simCode = ((commentsWeight * simComments) +
                   (100 - commentsWeight) * simCode) / 100

    featureMat, _ = featureMatrix(files)
    simFeatures = irp.calculateSimilarityByEuclideanMethod(featureMat, sigma=1)

    similarity = (0.8 * simCode + 0.2 * simFeatures) * 100
    sp.printProcessFinal(initial, 'Similarity calculated!')

    return similarity


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
            filesUpdated = []
            # Notify user
            if len(files) > 0:
                initial = sp.printProcessInitial('Processing files...')
            # Process features
            for file in files:
                err = file.processDocument()
                if err:
                    text = file.filename + ' : Invalid File!'
                    typer.secho(text, fg=typer.colors.RED)
                else:
                    filesUpdated.append(file)
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
            filesUpdated = []
            # Notify user
            if len(files) > 0:
                initial = sp.printProcessInitial('Processing files...')
            # Process features
            for file in files:
                err = file.processDocument()
                if err:
                    text = file.filename + ' : Invalid File!'
                    typer.secho(text, fg=typer.colors.RED)
                else:
                    filesUpdated.append(file)
            # Notify user
            if len(filesUpdated) > 0:
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
    if len(filesUpdated) != 0:
        result = calculateSimilarity(filesUpdated, pcomment)
        if rep == 'b':
            sp.representBinary(result, filesUpdated, [path1, path2])
        else:
            sp.representPrimary(result, filesUpdated, [path1, path2])
    else:
        text = 'No .' + filetype + ' files found!'
        typer.secho(text, fg=typer.colors.RED)


# Extract features of the code
# THE PATH MUST LEAD TO A FILE ONLY!
@app.command(help='Extract features from source code files.')
def extract(path: str = typer.Argument(..., help='Path to the file'), filetype: str = typer.Option(userpref['filetype'], help='The extension of the files to be processed')):
    filetype = filetype.lstrip('.')
    analyser = PathAnalyser(filetype)
    filetype, error = analyser.setExtension(path)

    if not error:
        fs = (analyser.processPath(path))[0]
        err = fs.extractFeatures()
        if err:
            text = fs.filename + ' : ' + err
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()
        result, features = featureMatrix([fs])
        df = pd.DataFrame(result, columns=[features], index=[fs.filename])
        typer.echo(df)
    else:
        text = path + ' : ' + error
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
