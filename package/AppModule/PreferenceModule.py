from os import path
import typer
from ..Analysers.PreferenceAnalyser import Preference


# App
app = typer.Typer()


# Set preferences
@app.command(help='Set user preference as required.')
def set(key: str = typer.Argument(..., help='Specify the key of the preference'), value: str = typer.Argument(..., help='Specify the value of the preference')):
    pref = Preference()
    if pref.check(key, value):
        if key == 'result_path':
            value = path.abspath(value)
        userpref = pref.initialize()
        userpref[key] = value
        pref.createPreferences(pref.getPreferencePath(), userpref)
        typer.secho('Preferences set!', fg=typer.colors.GREEN)
    else:
        typer.secho('Invalid preference key!', fg=typer.colors.RED)
        raise typer.Exit()


# Reset preferences
@app.command(help='Reset all the preferences to default values.')
def reset():
    pref = Preference()
    pref.resetPreferences(pref.getPreferencePath())
    typer.secho('Preferences set to default!', fg=typer.colors.GREEN)


# Display preferences
@app.command(help='Dsiplay all the preferences to the user.')
def show():
    pref = Preference()
    userpref = pref.initialize()
    for key, value in userpref.items():
        text = typer.style(key, fg=typer.colors.YELLOW) + \
            ' : ' + typer.style(value, fg=typer.colors.CYAN)
        typer.echo(text)


if __name__ == '__main__':
    app()
