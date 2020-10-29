from tkinter.filedialog import askopenfile
from pymongo import MongoClient
from tkinter import *
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

win64 = Label(window, text='Win64 URL : ')
win64.grid(row=2, column=0)
win64Field = Entry(window, width=100)
win64Field.grid(row=2, column=1, pady=5, padx=10)

darwin = Label(window, text='Darwin URL : ')
darwin.grid(row=3, column=0)
darwinField = Entry(window, width=100)
darwinField.grid(row=3, column=1, pady=5, padx=10)

debian = Label(window, text='Debian URL : ')
debian.grid(row=4, column=0)
debianField = Entry(window, width=100)
debianField.grid(row=4, column=1, pady=5, padx=10)


def generate_json(package_name : str ,win32 : str, win64 : str, darwin : str, debian : str):
    return {
        '_id': package_name,
        'package-name' : package_name,
        'win32' : win32,
        'win64' : win64,
        'darwin' : darwin,
        'debian' : debian,
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
    if package_name != '' and win32_url != '' and win64_url != '' and darwin_url != '' and debian_url != '':
        gen_json = generate_json(package_name, win32_url, win64_url, darwin_url, debian_url)
        manager = DatabaseManager()
        manager.write_data(gen_json)

file_select = Button(window, text='...', command=get_file_input)
file_select.grid(row=0, column=2)

window.bind('<Return>', upload_to_server)

window.mainloop()
