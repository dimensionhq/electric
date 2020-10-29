from subprocess import Popen, PIPE
from bson.json_util import dumps
from pymongo import MongoClient
from tempfile import gettempdir
from os.path import isfile
import time
import json

print('root :: Started Scanning For Changes')

client = MongoClient('mongodb+srv://TheBossProSniper:electricsupermanager@electric.kuixi.mongodb.net/<dbname>?retryWrites=true&w=majority')
collection = client['Electric']['Packages']

change_stream = client.changestream.collection.watch()

for change in change_stream:
    print('root :: Change Detected')
    res = dumps(change)
    json_res = json.loads(res)
    if json_res['operationType'] == 'insert':
        document = json_res['fullDocument']
        win32 = document['win32']
        win64 = document['win64']
        darwin = document['darwin']
        debian = document['debian']
        package_name = document['package-name']
        while True:
            if not isfile(f'{gettempdir()}\\automation.txt'):
                cmd = ['python', 'C:\\Users\\tejas\\Desktop\\electric\\Database\\automation.py', f'"{package_name}"', win32, win64, darwin, debian]
                proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                output, err = proc.communicate()
                output = output.decode('utf-8')
                output = output.replace("\'", "\"")
                response = json.loads(output)
                upload_loc = client['Electric']['Packages']
                upload_loc.insert_one(response)
                del_loc = client['changestream']['collection']
                del_loc.delete_one({ '_id' : f'{package_name}' })
                print('root :: Successfully Added Package To List')
                break
            else:
                time.sleep(5.0)
                continue
