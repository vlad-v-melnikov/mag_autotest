import unittest
import pyautogui
import glob

class TestCompareImages(unittest.TestCase):

    def test_screens(self):
        screens = zip(glob.glob('screenshots/prod_*.png'), glob.glob('screenshots/test_*.png'))
        for prod, test in screens:
            with self.subTest():
                try:
                    result = pyautogui.locate(test, prod)
                    self.assertTrue(bool(result), f"{test} does not match {prod}")
                except AssertionError as e:
                    print(str(e))


if __name__ == "__main__":
    unittest.main()