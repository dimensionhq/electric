from timeit import default_timer as timer
from psutil import *
from subprocess import *


class SystemManager:
    @staticmethod
    def get_pc_config():
        configuration = {}
        mem = virtual_memory()
        cpu_name, _ =  Popen('wmic cpu get name', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        configuration['cpu-info'] = cpu_name.decode('utf-8').replace('Name', '').replace('\r', '').replace('\n', '')[33:][:-2]
        configuration['memory'] = round(mem.total / 1000000000, 1)
        return configuration
