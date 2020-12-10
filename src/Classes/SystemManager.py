from subprocess import *


class SystemManager:
    @staticmethod
    def get_pc_config():
        configuration = {}
        cpu_name, _ =  Popen('wmic cpu get name', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        configuration['cpu-info'] = cpu_name.decode('utf-8').replace('Name', '').replace('\r', '').replace('\n', '')[33:][:-2]
        return configuration
