import json

# publisher, description = '', ''
# packages, editor_configuration, editor_extensions, pip_packages = {}, {}, {}, {}

d = {}
with open('test.electric', 'r') as f:
    chunks = f.read().split("\n\n")

    for chunk in chunks:
        chunk = chunk.replace("=>", ":").split('\n')
        header = chunk[0].replace("[", '').replace(']', '').strip()
        d[header] = []

        for line in chunk[1:]:
            try:
                k, v = line.split(":")
                k, v = k.strip(), v.strip()
            except ValueError:
                if header in ['Packages', 'Pip-Packages', 'Editor-Extensions']:
                    k, v = line, "latest"
            
            d[header].append({k: v.replace('"', '')})

print(json.dumps(d))