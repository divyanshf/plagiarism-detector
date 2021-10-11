import typer
import os
import sys
import stat
import pathlib


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
            userpref = self.resetPreferences(path)
        return userpref

    # Reset preferences
    def resetPreferences(self, path):
        userpref = dict()
        userpref['filetype'] = 'cpp'
        userpref['threshold'] = str(20)
        userpref['result_path'] = str(path)
        userpref['comment_weight'] = str(5)
        self.createPreferences(path=path, userpref=userpref)
        return userpref

    # Check if file
    def isFile(self, path):
        if os.path.isfile(path):
            return True
        return False

    # Check for key, value validity
    def check(self, key, value):
        if key in self.validKeys:
            if key == 'result_path':
                if os.path.exists(value):
                    return True
                else:
                    typer.secho('Path does not exist!', fg=typer.colors.RED)
                    raise typer.Exit()
            elif key == 'filetype':
                if value == 'cpp' or value == 'java':
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
            elif key == 'comment_weight':
                value = float(value)
                if value in range(0, 10):
                    return True
                else:
                    typer.secho('Invalid comment weight!', fg=typer.colors.RED)
                    raise typer.Exit()
        else:
            return False

    # Get preference path for platform
    def getPreferencePath(self):
        if sys.platform == 'linux':
            return self.home / '.config' / 'plag'
        elif sys.platform == 'win32':
            return self.home / 'AppData' / 'plag'
        elif sys.platform == 'darwin':
            return self.home / 'Library' / 'Application Support' / 'plag'
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
            if(key == 'result_path'):
                try:
                    value = os.path.abspath(value)
                except:
                    typer.secho(str("Invalid value"), fg=typer.colors.RED)
                    raise typer.Exit()
            prefs += key+'='+value+'\n'
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            if os.path.isfile(path/'pref.txt'):
                os.chmod(path/'pref.txt', stat.S_IWUSR)
            with open(path/'pref.txt', 'w') as file:
                file.write(prefs)
                file.close()
                os.chmod(path/'pref.txt', 0o444)
        except Exception as ex:
            typer.secho(str(ex), fg=typer.colors.RED)
            raise typer.Exit()
