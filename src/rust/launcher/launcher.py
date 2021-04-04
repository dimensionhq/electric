# from colorama import Fore
from tempfile import gettempdir
import requests
import sys
import os

sys.argv[1] = sys.argv[1].replace('electric:', '')
url = sys.argv[1].split(',')[0].split('=')[1]
config_name = sys.argv[1].split(',')[1].split('=')[1]

if not os.path.isdir(rf'{gettempdir()}\electric'):
    os.mkdir(rf'{gettempdir()}\electric')

if not os.path.isdir(rf'{gettempdir()}\electric\configurations'):
    os.mkdir(rf'{gettempdir()}\electric\configurations')


def download_file(url: str, name: str) -> str:
    
    file = rf'{gettempdir()}\electric\configurations\{name}.electric'
    
    with open(file, "wb") as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')
        
        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % (f'=' * done, '-' * (50-done)) )    
                sys.stdout.flush()
    
    return file

print(f'Downloading {config_name}.electric from {url}')
fp = download_file(url, config_name)
sys.stdout.write('\n')
print(fp)
print(f'electric config "{fp}"')
os.system(rf'electric config "{fp}"')
sys.exit()