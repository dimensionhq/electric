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
    
    res = dumps(change)
    json_res = json.loads(res)
    if json_res['operationType'] == 'insert':
        document = json_res['fullDocument']
        json_name = list(document.keys())[1]
        document = document[json_name]
        win32 = document['win32']
        win64 = document['win64']
        darwin = document['darwin']
        debian = document['debian']
        win32_type = document['win32-type']
        win64_type = document['win64-type']
        darwin_type = document['darwin-type']
        debian_type = document['debian-type']
        package_name = document['package-name']

        while True:
            if not isfile(f'{gettempdir()}\\automation.txt'):
                print('root :: Executing Automation Script')
                cmd = ['python', 'C:\\Users\\tejas\\Desktop\\electric\\Database\\automation.py', f'"{package_name}"', win32, win64, darwin, debian, win32_type, win64_type, darwin_type, debian_type, json_name]
                proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                output, err = proc.communicate()
                output = output.decode('utf-8')
                output = output.replace("\'", "\"")
                upload_loc = client['Electric']['Packages']
                # Old Json File
                old_json = upload_loc.find_one()
                if old_json and old_json != '' and old_json != '{}':
                    current_json = old_json
                    # Delete Old Json File
                    upload_loc.delete_one(current_json)
                    # New Json File
                    response = json.loads(output)
                    name = list(response.keys())[0]
                    current_json.__setitem__(name, response[name])

                    print('root :: Uploading To Database')
                    upload_loc.insert_one(current_json)
                    del_loc = client['changestream']['collection']
                    count = del_loc.delete_many({})
                    print('root :: Successfully Added Package To List')
                    break
                else:
                    response = json.loads(output)
                    upload_loc.insert_one(response)
                    del_loc = client['changestream']['collection']
                    count = del_loc.delete_many({})
                    break
            else:
                print('root :: Found automation.txt File, Aborting Process')
                time.sleep(5.0)
                continue
