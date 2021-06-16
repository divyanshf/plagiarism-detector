from msvcrt import getch
from os import system, name
from sys import platform
from colorama import init, deinit
from colorama.ansi import Fore, Style


def initialize():
    init()


def deinitialize():
    deinit()


def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


# Keyboard
class KeyboardStuff:
    def __init__(self):
        self.platform = platform
        self.keyBinds = {b'H': 'up', b'P': 'down', b'M': 'right', b'K': 'left'}

    def detectKey(self):
        if self.platform == 'win32':
            import msvcrt
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\x00' or key == b'\xe0':
                        ch = self.keyBinds[msvcrt.getch()]
                        return ch
                    else:
                        return key
        else:
            print('Not supported platform')
            exit(0)


# Menu Class to show a menu
class Menu:
    def __init__(self, options, current, title):
        self.options = options
        self.current = current
        self.title = title

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
        keyboard = KeyboardStuff()
        while True:
            ch = keyboard.detectKey()
            if ch == 'up':
                self.moveUp()
            elif ch == 'down':
                self.moveDown()
            elif ch == b'\r':
                break
        return self.current

    # Render
    def render(self):
        clear()
        print(Style.RESET_ALL + self.title)
        for index, option in enumerate(self.options):
            if self.current == index:
                print(Fore.GREEN + '->', end='')
            else:
                print(Fore.CYAN + '  ', end='')
            print(option + Style.RESET_ALL)
