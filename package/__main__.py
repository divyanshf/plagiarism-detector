from os import error
from typing import Optional
import typer
from .Analyser import PathAnalyser
from .IREProcessor import IREProcessor
import pandas as pd


# Typer app
app = typer.Typer()


# Process corpus
def processCorpus(corpus, filenames, globalForm):
    irp = IREProcessor()

    tdMatrix = irp.createTermDocumentMatrix(corpus)
    df = pd.DataFrame(tdMatrix)
    typer.echo(df)

    tdMatrix = irp.applyWeighting(tdMatrix, globalForm)

    similarity = irp.calculateSimilarity(tdMatrix)
    return similarity


# Calculate similarity
def calculateSimilarity(files):
    corpusCode = [doc.file for doc in files]
    # corpusComment = [doc.comments for doc in files]
    filenames = [doc.filename for doc in files]
    simCode = processCorpus(corpusCode, filenames, 'normal')
    result = simCode[0, :] * 100
    columns = ['Sim(Code)']
    return result, columns


# Detect similarity
# SINGLE PATH : FOLDER
# TWO PATHS : TWO FILES OR ONE FILE - ONE FOLDER
@app.command()
def compare(path1: str = typer.Argument(..., help='Path to a file or folder'), path2: str = typer.Argument('', help='Path to a file or folder'), filetype: str = typer.Argument('cpp', help='The extension of the files to be processed')):
    # Remove leading period sign from the filetype
    filetype = filetype.lstrip('.')

    analyser = PathAnalyser(filetype)

    # Check for single path
    if path2 == '':
        isDir, error = analyser.isDir(path1)
        if isDir:
            files = analyser.processPath(path1)
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

    result, columns = calculateSimilarity(files)
    df = pd.DataFrame(result, columns=columns)
    typer.echo(df)


# Extract features of the code
# THE PATH MUST LEAD TO A FILE ONLY!
@app.command()
def extract(path: str = typer.Argument(..., help='Path to the file')):
    analyser = PathAnalyser()
    filetype, error = analyser.setExtension(path)
    if filetype:
        fs = (analyser.processPath(path))[0]
        fs.processDocument()
    else:
        text = path + ' : ' + error
        typer.secho(text, fg=typer.colors.RED)
        raise typer.Exit()


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
