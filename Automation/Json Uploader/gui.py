from tkinter import *
from pymongo import MongoClient

class DatabaseManager:
    def write_data(self, data : str):
        cluster = MongoClient('mongodb+srv://TheBossProSniper:electricsupermanager@electric.kuixi.mongodb.net/<dbname>?retryWrites=true&w=majority')
        db = cluster['Electric']
        collection = db['Packages']
        collection.insert_one(data)


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


def upload_to_server():
    package_name = nameField.get()
    win32_url = win32Field.get()
    win64_url = win64Field.get()
    darwin_url = darwinField.get()
    debian_url = debianField.get()
    if package_name != '' and win32_url != '' and win64_url != '' and darwin_url != '' and debian_url != '':
        gen_json = generate_json(package_name, win32_url, win64_url, darwin_url, debian_url)
        manager = DatabaseManager()
        manager.write_data(gen_json)


submit = Button(window, text='Submit', width=15, height=1, command = upload_to_server)
submit.grid(row=5, column=1, pady=10)

window.mainloop()
