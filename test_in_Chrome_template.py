import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class TestInChrome(unittest.TestCase):

    def setUp(self) -> None:
        self.driver_prod = webdriver.Chrome()

    def tearDown(self):
        self.driver_prod.close()


if __name__ == "__main__":
    unittest.main()
