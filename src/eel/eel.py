from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from eel_cli import SuperChargeCLI
from moviepy.editor import VideoClipFile
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
        if quality == 'high':
            bitrate = '300k'
        elif quality == 'low':
            bitrate = '80k'
        elif quality == 'medium':
            bitrate = '200k'
        elif quality == 'ultra-high':
            bitrate = '800k'
        elif quality == 'ultra-low':
            bitrate = '30k'
        video = VideoFileClip(file_path)
        video.audio.write_audiofile(destination, bitrate=bitrate)
