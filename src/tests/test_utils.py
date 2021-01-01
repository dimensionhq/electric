import unittest
import utils
from Classes.Setting import Setting



class TestUtil(unittest.TestCase):

    def test_is_admin(self):
        self.assertIsNotNone(utils.is_admin())
    
    def test_send_req_bundle(self):
        res, _ = utils.send_req_bundle()
        pkg_data = res['atom']
        self.assertIsNotNone(pkg_data, msg="Package is missing or Request Failed")
    
    # def test_download(self):
    #     metadata = utils.generate_metadata(
    #     False, False, False, False, False, False, '', False, False, 0, Setting.new())
    # #     metadata = Metadata(False, False, False, False, False, False, '', False, False, 0, Setting({
    # #     "$schema": "http://electric-package-manager.herokuapp.com/schemas/settings",
    # #     "progressBarType": "accented",
    # #     "showProgressBar": True,
    # #     "electrifyProgressBar": False,
    # #     "customProgressBar":{
    # #         "unfill_character": ' ',
    # #     }
    # # },
    # # progress_bar_type = 'default',
    # # show_progress_bar = False,
    # # electrify_progress_bar = False,
    # # use_custom_progress_bar = False,
    # # custom_progress_bar = None
    # # ))
    #     res = utils.download('abcdef', 'atom', metadata,'')
    #     print(res)



if __name__ == "__main__":
    unittest.main()