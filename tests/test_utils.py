import unittest
import utils

class TestUtil(unittest.TestCase):

    def test_is_admin(self):
        self.assertIsNotNone(utils.is_admin())

    def test_send_req_bundle(self):
        res, _ = utils.send_req_bundle()
        pkg_data = res['atom']
        self.assertIsNotNone(pkg_data, msg="Package is missing or Request Failed")

    def test_package_request(self):
        res, time  = utils.send_req_package('atom')
        self.assertIsNotNone(time)
        self.assertIsNotNone(res)

    def test_version_check(self):
        newer_version = utils.check_newer_version('9.0.1')
        self.assertIs(newer_version, True)


    def test_gen_metadata(self):
        meta = utils.generate_metadata(None, None, None, None, None, None, None, None, None, None, None)
        self.assertIsInstance(meta, utils.Metadata)

    def test_check_supercache_availiable(self):
        availiable = utils.check_supercache_availiable('atom')
        self.assertIsInstance(availiable, bool)

    def test_display_info(self):
        res, _ = utils.send_req_package('atom')
        text = utils.display_info(res)
        self.assertIsInstance(text, str)
        res, _ = utils.send_req_package('atom')
        text = utils.display_info(res, nightly=True)
        self.assertIsInstance(text, str)

    def test_get_correct_package_names(self):
        packages = utils.get_correct_package_names()
        self.assertIsInstance(packages, list)

    def test_autocorrections(self):
        corrections = utils.get_autocorrections(
            ['ato', 'sublime-text'], utils.get_correct_package_names(all=True), utils.Metadata(None, None, True, True, None, None, None, None, None, None, None))
        self.assertIsInstance(corrections, list)
    
    def test_send_req_package(self):
        package = 'atom'
        response, time = utils.send_req_package(package)
        self.assertIsNotNone(response)
        self.assertIsNotNone(time)

if __name__ == "__main__":
    unittest.main()
