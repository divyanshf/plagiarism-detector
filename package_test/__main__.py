from os import path
from typing import Optional
import typer
from .Analyse import PathAnalyser

app = typer.Typer()


# Detect similarity
@app.command()
def compare(path1: str = typer.Argument(..., help='Path to the primary file'), path2: str = typer.Argument(..., help='Path to another file or folder'), filetype: str = typer.Argument('cpp', help='The extension of the files to be processed')):
    analyser = PathAnalyser(filetype)
    isFile1, error = analyser.isFile(path1)
    if isFile1:
        files = analyser.processPath(path1) + analyser.processPath(path2)
    else:
        text = path1 + ' : ' + error
        typer.secho(text, fg=typer.colors.RED)
        raise typer.Exit()
    typer.echo('DONE')


# Extract features of the code
@app.command()
def extract(path: str = typer.Argument(..., help='Path to the file')):
    typer.echo('Extract features.')


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
