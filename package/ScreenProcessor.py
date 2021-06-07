from os import system, name
from typing import Optional
from colorama import init, deinit
from colorama.ansi import Fore, Style
import keyboard


def initialize():
    init()


def deinitialize():
    deinit()


def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


# Menu Class to show a menu
class Menu:
    def __init__(self, options, current):
        self.options = options
        self.current = current

    # Move the cursor up
    def moveUp(self):
        self.current = self.current - 1 if self.current != 0 else 0
        self.render()

    # Move the cursor down
    def moveDown(self):
        self.current = self.current + \
            1 if self.current != len(self.options) - \
            1 else len(self.options) - 1
        self.render()

    # Take input
    def takeInput(self):
        keyboard.add_hotkey('up', self.moveUp)
        keyboard.add_hotkey('down', self.moveDown)
        keyboard.wait('enter')
        # clear()
        keyboard.remove_all_hotkeys()
        return self.current

    # Render
    def render(self):
        clear()
        for index, option in enumerate(self.options):
            if self.current == index:
                print(Fore.GREEN + '->', end='')
            else:
                print(Fore.CYAN + '  ', end='')
            print(option + Style.RESET_ALL)
