import sys
import json
import requests
from colorama import Fore
from bs4 import BeautifulSoup
from pygments import highlight, lexers, formatters
import re

from requests.models import parse_url

def swc(url: str):
    res = requests.get(url)
    return res.text

message = '''AU - The Official Electric Auto-Update CLI For Generating Automatically Updating Manifests.
'''
print(message)

print('Enter the path to the manifest / json file: ')
fp = input(F'>{Fore.LIGHTYELLOW_EX} ').replace('\"', '')

with open(fp, 'r') as f:
    data = json.load(f)

package_name = data['package-name']

latest_version = data['latest-version']

webpage = data['auto-update']['vercheck']['webpage']

print(f'{Fore.LIGHTGREEN_EX}Sending Request To {webpage}{Fore.RESET}')

html = swc(webpage.strip())
show_html = input(
    'Would you like to see the response of the request? [Y/n]: ')
if show_html == 'y' or show_html == 'Y' or show_html == 'yes' or show_html == 'YES' or show_html == 'Yes':
    print(highlight(html, lexers.HtmlLexer(), formatters.TerminalFormatter()))

soup = BeautifulSoup(html, features="html.parser")

if webpage.startswith('https://www.github.com'):
    version_list = {}
    
    for tag in soup.find_all('h4', class_='flex-auto min-width-0 pr-2 pb-1 commit-title'):
        if tag:
            try:
                version_list[tag.find('a').text.strip().replace('v', '').replace('V', '')] = int(
                    tag.find('a').text.strip().replace('.', '').replace('v', '').replace('V', ''))
            except:
                    pass
                    
    print(f'Detected Versions On Webpage:', list(version_list.keys()))

    try:
        web_version = max(version_list, key=version_list.get)
    except:
        print(f'{Fore.LIGHTRED_EX}No Versions Detected On Webpage!{Fore.RESET}')
        if webpage.startswith('https://www.github.com'):
            print('You must send a web request to /tags not /releases. For example: https://github.com/atom/atom/tags not https://github.com/atom/atom/releases')
        sys.exit()

    print(f'{Fore.LIGHTGREEN_EX}Latest Version Detected:{Fore.RESET} {web_version}')

    int_web_version = int(web_version.strip().replace(
        'v', '').replace('V', '').replace('.', ''))

    try:
        int_current_version = int(latest_version.strip().replace(
            'v', '').replace('V', '').replace('.', ''))
    except:
        print(f'{Fore.LIGHTRED_EX}The Current Version Must Not Contain Any Characters')

    if int_current_version < int_web_version:
        print(
            f'A Newer Version Of {package_name} Is Availiable! Updating Manifest')

        old_latest = latest_version
        data['latest-version'] = web_version
        data[web_version] = data[old_latest]
        data[web_version]['url'] = data['auto-update']['url'].replace(
            '<version>', web_version)
        from pygments import highlight, lexers, formatters
        
        formatted_json = json.dumps(data, indent=4)

        colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)

        with open(fp, 'w+') as f:
            f.write(formatted_json)

else:
    result = re.findall(data['auto-update']['vercheck']['regex'], html)
    version = result[0]
    res_tup = []

    idx = 1
    for value in version:
        res_tup.append({f'<{idx}>' : value})
        idx += 1

    replace = data['auto-update']['vercheck']['replace']

    for value in res_tup:
        replace = replace.replace(list(value.keys())[0], list(value.values())[0])

    url = data['auto-update']['url']

    url = url.replace('<version>', replace)

    for value in res_tup:
        url = url.replace(list(value.keys())[0], list(value.values())[0])

    print(url)