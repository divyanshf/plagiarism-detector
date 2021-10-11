import typer
import datetime
import os
import pathlib
import pandas as pd
import numpy as np


class ScreenProcessor:
    def __init__(self, userpref):
        self.userpref = userpref

    def printProcessInitial(self, initial):
        text = '-> ' + initial
        typer.secho(text + '\r', nl=False, fg=typer.colors.YELLOW)
        return text

    def printProcessFinal(self, initial, final):
        empString = ' ' * len(initial)
        empString = empString + '\r'
        typer.echo(empString, nl=False)
        text = '-> ' + final
        typer.secho(text, fg=typer.colors.GREEN)

    # Save results to a csv file
    def saveResults(self, dataframe, paths):
        timestamp = datetime.datetime.now()
        date = timestamp.strftime("%Y-%m-%d")
        time = timestamp.strftime("%I-%M-%S %p")
        result_path = pathlib.Path(self.userpref['result_path'])
        basepath = result_path / date / time
        try:
            if not(os.path.exists(basepath)):
                os.makedirs(basepath)
            # os.chmod(path, stat.S_IRWXO)
            path = basepath / 'result.csv'
            dataframe.to_csv(path)
            with open(basepath / 'readme.txt', 'w') as file:
                text = ''
                for path in paths:
                    if path:
                        text = text + 'Input : ' + os.path.abspath(path) + '\n'
                text = text + 'Preferences used:\n'
                for key, value in self.userpref.items():
                    text = text + key + ' : ' + value + '\n'
                file.write(text)
                file.close()
            result = 'Saved to ' + str(basepath)
            typer.secho(result, fg=typer.colors.GREEN)
        except Exception as ex:
            typer.secho(str(ex), fg=typer.colors.RED)
            raise typer.Exit()

    # Represent max two sims
    def representBinary(self, sims, files, paths):
        threshold = float(self.userpref['threshold'])
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
            self.saveResults(df, paths)
        else:
            typer.secho('NO PLAGIARISM ABOVE THRESHOLD FOUND.',
                        fg=typer.colors.GREEN)

    # Represent multiple file sims
    def representPrimary(self, simCode, files, paths):
        threshold = float(self.userpref['threshold'])
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
        self.saveResults(df, paths)
