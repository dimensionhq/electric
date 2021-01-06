import unittest
from subprocess import Popen, PIPE
import subprocess

class TestElectricCli(unittest.TestCase):
    
    # These tests assume that electric is currently installed on the host machine 
    # and is in operable condition. Deal with errors while bearing this in mind. 

    def test_electric_search(self):
        proc = Popen('electric search atom'.split(),
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err2 = proc.communicate()
        self.assertIn('atom', output.decode().splitlines())
    
    def test_electric_cleanup(self):
        s = subprocess.check_call('electric cleanup',stdout=PIPE)
        self.assertIs(s, 0)
        

if __name__ == '__main__':
    unittest.main()
