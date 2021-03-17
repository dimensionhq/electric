######################################################################
#                             VIRUS CHECK                            #
######################################################################


import requests
import hashlib

API_KEY = 'GET'

def virus_check(path : str):
    """
    Uses the virustotal api to check if a file contains viruses.

    #### Arguments
        path (str): The path to the file to check for viruses

    Returns:
        result (dict): The virustotal api response
    """
    
    # Read A .exe File
    with open(rf'{path}', 'rb') as f:
        content = f.read()
        EICAR = content

    # Read a .py File
    # with open(R'C:\Users\xtrem\Desktop\electric\setup.py', 'r') as f:
    #     content = f.read()
    #     EICAR = content.encode('utf-8')

    EICAR_MD5 = hashlib.md5(EICAR).hexdigest()
    URL = 'https://electric-package-manager-api.herokuapp.com/virus-check/' + EICAR_MD5
    res = requests.post(URL)
    return res.json()
