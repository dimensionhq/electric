import unittest
from subprocess import Popen, PIPE

class TestElectricCli(unittest.TestCase):
    def test_electric_show(self):
        proc = Popen('electric search atom'.split(),
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, _ = proc.communicate()
        self.assertIn('atom', output.decode().splitlines())

if __name__ == '__main__':
    unittest.main()
