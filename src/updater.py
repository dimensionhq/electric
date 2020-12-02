######################################################################
#                               UPDATER                              #
######################################################################

import shutil
import py7zr
import os   


archive = py7zr.SevenZipFile(R'C:\Program Files (x86)\Electric\Update.7z', 'r')
archive.extractall(R'C:\Program Files (x86)\Electric\latest')
archive.close()
os.remove(R'C:\Program Files (x86)\Electric\Update.7z')
shutil.rmtree(R'C:\Program Files (x86)\Electric\bin')
shutil.move(R'C:\Program Files (x86)\Electric\latest\bin', R'C:\Program Files (x86)\Electric')
shutil.rmtree(R'C:\Program Files (x86)\Electric\latest')
