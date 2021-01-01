import unittest
import registry

class TestRegistry(unittest.TestCase):

    def test_get_uninstall_key(self):
        ans = registry.get_uninstall_key('sublime-text-3', 'Sublime Text 3')
        self.assertIsInstance(ans, list)

    def test_get_environment_keys(self):
        #TODO: work on this og function...
        ans = registry.get_environment_keys()
        self.assertIsNotNone(ans)

if __name__ == "__main__":
    unittest.main()