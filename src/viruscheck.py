######################################################################
#                             VIRUS CHECK                            #
######################################################################


from virus_total_apis import PublicApi as VTApi
import hashlib

API_KEY = '776bd8a0f128d2f425b821524dce5b2d43904bff15a467c8b332ac2561e9624b'


def virus_check(path : str):
    # Read A .exe File
    with open(rf'{path}', 'rb') as f:
        content = f.read()
        EICAR = content

    # Read a .py File
    # with open(R'C:\Users\tejas\Desktop\electric\setup.py', 'r') as f:
    #     content = f.read()
    #     EICAR = content.encode('utf-8')

    EICAR_MD5 = hashlib.md5(EICAR).hexdigest()

    vt = VTApi(API_KEY)

    res = vt.get_file_report(EICAR_MD5)
    keys = list(res.keys())
    data = res[keys[0]]['scans']

    detected = {}

    for value in data.items():
        if value[1]['detected'] == True:
            detected.update({value[0] : value[1]['result']})

    return detected

