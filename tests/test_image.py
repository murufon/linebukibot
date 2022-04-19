# coding:utf-8

import unittest
import json
import os

class ImageTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_main(self):
        with open('weapon.json', 'r') as f:
            json_data = json.load(f)
        for buki in json_data:
            path = "static/twitter_images_orig/" + buki["name"]["ja_JP"] + ".jpg"
            self.assertTrue(os.path.isfile(path), f"{path} does not exist")
            path = "static/twitter_images_small/" + buki["name"]["ja_JP"] + ".jpg"
            self.assertTrue(os.path.isfile(path), f"{path} does not exist")

if __name__ == "__main__":
    unittest.main()
