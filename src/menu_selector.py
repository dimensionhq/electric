# Menu Selector
import keyboard
import click
from colorama import Back
import sys
import subprocess
from subprocess import PIPE

index = 0
final_value = None


def show_menu_selector(executable_list, file_path):
    def trigger():
        click.clear()
        for executable in executable_list:
            if executable == executable_list[index]:
                print(Back.CYAN + executable + Back.RESET)
            else:
                print(executable)

    trigger()
    # print('You have selected: ', executable_list[index])

    def up():
        global index
        if len(executable_list) != 1:
            index -= 1
            if index >= len(executable_list):
                index = 0
                trigger()
                return
            trigger()

    def down():
        global index
        if len(executable_list) != 1:
            index += 1
            if index >= len(executable_list):
                index = 0
                trigger()
                return
            trigger()

    def enter():
        if executable_list[index] == 'Exit':
            click.echo('Press Control + C To Confirm Quitting...')
            sys.exit()
        path = file_path + "\\" + executable_list[index]
        click.echo(click.style(f'Running {executable_list[index]}. Hit Control + C to Quit', fg='magenta'))
        subprocess.call(path, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        quit()

    keyboard.add_hotkey('up', up)
    keyboard.add_hotkey('down', down)
    keyboard.add_hotkey('enter', enter)
    keyboard.wait()

