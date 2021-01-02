from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from eel_cli import SuperChargeCLI
from moviepy.editor import *
import click


conversions = [
    'mp4 => mp3',
    'mp4 => wav'
]

@click.group(cls=SuperChargeCLI)
def cli():
    pass

@cli.command(aliases=['conv'])
def convert():
    conversion_completer = WordCompleter(conversions)
    convert = prompt('>>> ', completer=conversion_completer)
    key, value = f"{convert.split('=>')[0].strip()}", f"{convert.split('=>')[1].strip()}"
    file_path = prompt(f'Location To {key} File >>> ')
    destination = prompt(f'Destination {value} File >>> ')
    if key == 'mp4' and value == 'mp3':
        quality = prompt('Audio Quality >>> ',completer=WordCompleter(['ultra-low', 'low', 'medium', 'high', 'ultra-high']))
        if quality == 'ultra-low':
            bitrate = '30k'
        if quality == 'low':
            bitrate = '80k'
        if quality == 'medium':
            bitrate = '200k'
        if quality == 'high':
            bitrate = '300k'
        if quality == 'ultra-high':
            bitrate = '800k'
        video = VideoFileClip(file_path)
        video.audio.write_audiofile(destination, bitrate=bitrate)
