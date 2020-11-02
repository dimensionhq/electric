from tkinter.filedialog import askopenfile
from pymongo import MongoClient
from tkinter import *
import re
import json

class DatabaseManager:
    def write_data(self, data : str):
        cluster = MongoClient('mongodb+srv://TheBossProSniper:electricsupermanager@electric.kuixi.mongodb.net/<dbname>?retryWrites=true&w=majority')
        db = cluster['changestream']
        collection = db['collection']
        collection.insert_one(data)
        label = Label(window, text='Successfully Uploaded To Server')
        label.config(fg='green')
        label.grid(row=6, column=1, pady=10)


window = Tk()
window.title('JSON Uploader')

name = Label(window, text='Package Name : ')
name.grid(row=0, column=0)
nameField = Entry(window, width=30)
nameField.grid(row=0, column=1, pady=5)

win32 = Label(window, text='Win32 URL : ')
win32.grid(row=1, column=0)
win32Field = Entry(window, width=100)
win32Field.grid(row=1, column=1, pady=5, padx=10)
win32var = StringVar(window)
win32var.set('.exe')
win32Type = OptionMenu(window, win32var, '.zip', '.msi')
win32Type.grid(row=2, column=1, pady=5, padx=10)


win64 = Label(window, text='Win64 URL : ')
win64.grid(row=3, column=0)
win64Field = Entry(window, width=100)
win64Field.grid(row=3, column=1, pady=5, padx=10)
win64var = StringVar(window)
win64var.set('.exe')
win64Type = OptionMenu(window, win64var, '.zip', '.msi')
win64Type.grid(row=4, column=1, pady=5, padx=10)


darwin = Label(window, text='Darwin URL : ')
darwin.grid(row=5, column=0)
darwinField = Entry(window, width=100)
darwinField.grid(row=5, column=1, pady=5, padx=10)
darwinvar = StringVar(window)
darwinvar.set('.dmg')
darwinType = OptionMenu(window, darwinvar, '.pkg', '.zip', '.tar.gz')
darwinType.grid(row=6, column=1, pady=5, padx=10)


debian = Label(window, text='Debian URL : ')
debian.grid(row=7, column=0)
debianField = Entry(window, width=100)
debianField.grid(row=7, column=1, pady=5, padx=10)
debianvar = StringVar(window)
debianvar.set('.deb')
debianType = OptionMenu(window, debianvar, '.tar.gz', '.zip', '.tar.xz', '.tar.bz2')
debianType.grid(row=8, column=1, pady=5, padx=10)

def smart_detect_type():

    win32 = win32Field.get()
    win64 = win64Field.get()
    darwin = darwinField.get()
    debian = debianField.get()

    win32_type = None

    if '.exe' in win32:
        win32_type = '.exe'
    if '.msi' in win32:
        win32_type = '.msi'
    if '.zip' in win32:
        win32_type = '.zip'

    win64_type = None
    if '.exe' in win64:
        win64_type = '.exe'

    if '.msi' in win64:
        win64_type = '.msi'

    if '.zip' in win64:
        win64_type = '.zip'

    darwin_type = None
    if '.dmg' in darwin:
        darwin_type = '.dmg'

    if '.pkg' in darwin:
        darwin_type = '.pkg'

    if '.tar.gz' in darwin:
        darwin_type = '.tar.gz'

    debian_type = None
    if '.deb' in debian:
        debian_type = '.deb'

    if '.tar.gz' in debian:
        debian_type = '.tar.gz'

    if '.tar.bz2' in debian:
        debian_type = '.tar.bz2'

    if '.tar.xz' in debian:
        debian_type = '.tar.xz'

    if win32 != '':
        if not win32_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", win32)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)

            if matches != '.zip' or matches != '.exe' or matches != '.msi':
                pass
            else:
                win32_type = extension

    if win64 != '':
        if not win64_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", win64)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)

            if matches != '.zip' or matches != '.exe' or matches != '.msi':
                pass
            else:
                win64_type = extension

    if darwin != '':
        if not darwin_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", darwin)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)

            if matches != '.zip' or matches != '.dmg' or matches != '.pkg' or matches != '.tar.gz':
                pass
            else:
                darwin_type = extension

    if debian != '':
        if not debian_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", debian)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)
            if matches != '.zip' or matches != '.exe' or matches != '.msi':
                pass
            else:
                debian_type = extension

    win32var.set([win32_type])
    win64var.set([win64_type])
    darwinvar.set([darwin_type])
    debianvar.set([debian_type])


smartDetect = Button(window, text='Smart Detect', command=smart_detect_type)
smartDetect.grid(row=9, column=1, pady=20)




def generate_json(package_name : str ,win32 : str, win64 : str, darwin : str, debian : str, win32_type : str, win64_type : str, darwin_type : str, debian_type : str):
    return {
        '_id': package_name,
        'package-name' : package_name,
        'win32' : win32,
        'win64' : win64,
        'darwin' : darwin,
        'debian' : debian,
        'win32-type': win32_type.replace('\'', '').replace('(', '').replace(')', '').replace(',', ''),
        'win64-type': win64_type.replace('\'', '').replace('(', '').replace(')', '').replace(',', ''),
        'darwin-type': darwin_type.replace('\'', '').replace('(', '').replace(')', '').replace(',', ''),
        'debian-type': debian_type.replace('\'', '').replace('(', '').replace(')', '').replace(',', ''),
    }

def get_file_input() -> str:
    file = askopenfile(mode = 'r', filetypes= [('JSON Files', '*.json')]).name
    contents = ''
    with open(file) as f:
        contents = f.read()
    res = json.loads(contents)
    pkg_n = list(res.keys())[0]
    nameField.delete(0, END)
    nameField.insert(END, res[pkg_n]['package-name'])
    win32Field.delete(0, END)
    win32Field.insert(END, res[pkg_n]['win32'])
    win64Field.delete(0, END)
    win64Field.insert(END, res[pkg_n]['win64'])
    darwinField.delete(0, END)
    darwinField.insert(END, res[pkg_n]['darwin'])
    debianField.delete(0, END)
    debianField.insert(END, res[pkg_n]['debian'])
    return res

def upload_to_server(event):
    package_name = nameField.get()
    win32_url = win32Field.get()
    win64_url = win64Field.get()
    darwin_url = darwinField.get()
    debian_url = debianField.get()
    win32_type = win32var.get()
    win64_type = win64var.get()
    darwin_type = darwinvar.get()
    debian_type = debianvar.get()
    print(debian_type)

    if package_name != '' and win32_url != '' and win64_url != '' and darwin_url != '' and debian_url != '':
        gen_json = generate_json(package_name, win32_url, win64_url, darwin_url, debian_url, win32_type, win64_type, darwin_type, debian_type)
        manager = DatabaseManager()
        manager.write_data(gen_json)

file_select = Button(window, text='...', command=get_file_input)
file_select.grid(row=0, column=2)

window.bind('<Return>', upload_to_server)

window.mainloop()
