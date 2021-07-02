import typer
import os
import sys
import stat
import glob
import pathlib
from .Processor.FileProcessor import FileStructure


class PathAnalyser:
    def __init__(self, filetype='cpp'):
        self.filetype = '.'+filetype

    # Find and set extension
    def setExtension(self, path):
        ext = (os.path.splitext(path))[1]
        if ext != '':
            self.filetype = ext
            return ext, None
        else:
            return None, 'Not a file!'

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
        self.validKeys = ['filetype', 'threshold', 'result_path']
        self.home = pathlib.Path.home()

    # Initialize everything
    def initialize(self):
        path = self.getPreferencePath()
        isFile = self.isFile(path/'pref.txt')
        if isFile:
            userpref = self.loadPreferences(path)
        else:
            self.resetPreferences(path)
        return userpref

    # Reset preferences
    def resetPreferences(self, path):
        userpref = dict()
        userpref['filetype'] = 'cpp'
        userpref['threshold'] = str(20)
        userpref['result_path'] = str(path)
        self.createPreferences(path=path, userpref=userpref)

    # Check if file
    def isFile(self, path):
        if os.path.isfile(path):
            return True
        return False

    # Check for key validity
    def check(self, key, value):
        if key in self.validKeys:
            if key == 'result_path':
                if os.path.exists(value):
                    return True
                else:
                    typer.secho('Path does not exist!', fg=typer.colors.RED)
                    raise typer.Exit()
            elif key == 'filetype':
                if value == 'cpp':
                    return True
                else:
                    typer.secho('Unsupported filetype!',
                                fg=typer.colors.RED)
                    raise typer.Exit()
            elif key == 'threshold':
                value = float(value)
                if value in range(1, 100):
                    return True
                else:
                    typer.secho('Invalid threshold!', fg=typer.colors.RED)
                    raise typer.Exit()
        else:
            return False

    # Get preference path for platform
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
        prefs = file.readlines()
        for pref in prefs:
            key, value = pref.split('=')
            key = key.lstrip()
            value = value.rstrip()
            result[key] = value
        file.close()
        return result

    # Create Preferences
    def createPreferences(self, path, userpref):
        prefs = ''
        for key, value in userpref.items():
            prefs += key+'='+value+'\n'
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            os.chmod(path/'pref.txt', stat.S_IWUSR)
            file = open(path/'pref.txt', 'w')
            file.write(prefs)
            file.close()
            os.chmod(path/'pref.txt', 0o444)
        except Exception as ex:
            typer.secho(str(ex), fg=typer.colors.RED)
            raise typer.Exit()
