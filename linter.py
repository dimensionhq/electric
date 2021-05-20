import json, os, sys

os.chdir(r'C:\Users\xtrem\Desktop\Electric\Electric Packages\packages')
for f in os.listdir():
    data = ''
    try:
        with open(f, 'r') as file: 
            data = json.load(file)
    except:
         continue

    linted = {
        'display-name': data['display-name'],
        'package-name': data['package-name'],
    }


    # Change Based On Version

    # Not Portable

    if 'portable' in list(data.keys()):
        linted['portable'] = {'latest-version': data['portable']['latest-version']}

        for version in list(data['portable'].keys()):
            if version not in ['latest-version', 'auto-update', 'package-name', 'display-name']:

                linted['portable'][version] = {'url': data['portable'][version]['url']}

                if 'checksum' in list(data['portable'][version].keys()):
                    linted['portable'][version]['checksum'] = data['portable'][version]['checksum']

                if 'file-type' in list(data['portable'][version].keys()):
                    linted['portable'][version]['file-type'] = data['portable'][version]['file-type']

                if 'pre-install' in list(data['portable'][version].keys()):
                    linted['portable'][version]['pre-install'] = data['portable'][version]['pre-install']

                if 'post-install' in list(data['portable'][version].keys()):
                    linted['portable'][version]['post-install'] = data['portable'][version]['post-install']

                for key in list(data['portable'][version].keys()):
                    if key not in list(linted['portable'][version].keys()):
                        linted['portable'][version][key] = data['portable'][version][key]

                print(json.dumps(linted, indent=4))
                # TODO: Handle Portable Section data['portable']