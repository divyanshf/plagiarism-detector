import typer
import sys
import os
import glob
import pathlib
from .Processor.FileProcessor import FileStructure


class PathAnalyser:
    def __init__(self, filetype='cpp'):
        self.filetype = '.'+filetype

    # Find and set extension
    def setExtension(self, path):
        try:
            ext = (os.path.splitext(path))[1]
            self.filetype = ext
            return ext, None
        except Exception as ex:
            return None, str(ex)

    # Check if the path is a file
    def isFile(self, path):
        error = ''
        if os.path.exists(path):
            if os.path.isfile(path):
                if (os.path.splitext(path))[1] == self.filetype:
                    return True, None
                else:
                    error = 'Incorrect File Extension!'
            else:
                error = 'Not a File!'
        else:
            error = 'Path does not exist!'
        return False, error

    # Check if the path is a directory
    def isDir(self, path):
        error = ''
        if os.path.exists(path):
            if os.path.isdir(path):
                return True, None
            else:
                error = 'Not a Directory'
        else:
            error = 'Path does not exist!'
        return False, error

    # Process the provided path for files
    def processPath(self, path):
        files = []

        if os.path.exists(path):
            # If the path is a file
            if os.path.isfile(path):
                extension = (os.path.splitext(path))[1]
                # Check if the extension is correct
                if extension == self.filetype:
                    fs = self.getFileStructure(path)
                    files.append(fs)
                else:
                    text = path + ' : Incorrect Extension!'
                    typer.secho(text, fg=typer.colors.RED)
                    raise typer.Exit()
            # If the path is a directory
            elif os.path.isdir(path):
                files += self.checkDirectory(path)
        else:
            text = path + ' does not exist!'
            typer.secho(text, fg=typer.colors.RED)
            raise typer.Exit()

        return files

    # Check the directory for files and return all that match
    def checkDirectory(self, path):
        files = []
        os.chdir(path)
        ext = '*'+self.filetype
        for file in glob.glob(ext):
            fs = self.getFileStructure(file)
            files.append(fs)
        return files

    # Get the file structure for a file
    def getFileStructure(self, path):
        _, filename = os.path.split(path)
        file = open(path, 'r')
        fs = FileStructure(filename, file, self.filetype)
        return fs


# Preference Format
# key=value
class Preference:
    # Get user preferences
    def __init__(self) -> None:
        self.home = pathlib.Path.home()

    def isFile(self, path):
        if os.path.isfile(path):
            return True
        return False

    def getPreferencePath(self):
        if sys.platform == 'linux':
            return self.home / '.conifg/plag'
        elif sys.platform == 'win32':
            return self.home / 'AppData/plag'
        elif sys.platform == 'darwin':
            return self.home / 'Library/Application Support/plag'
        else:
            typer.secho('Platform not supported yet!', fg=typer.colors.RED)
            raise typer.Exit()

    # Load Preferences
    def loadPreferences(self, path):
        result = dict()
        file = open(path/'pref.txt')
        content = file.readlines()
        typer.echo(content)

    # Create Preferences
    def createPreferences(self, path, userpref):
        pref = 'filetype='+userpref['filetype']+'\n'
        if not os.path.isfile(path/'pref.txt'):
            os.makedirs(path)
        try:
            file = open(path/'pref.txt', 'w')
            file.write(pref)
            file.close()
        except Exception as ex:
            typer.secho(str(ex), fg=typer.colors.RED)
