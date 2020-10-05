import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class TestInFirefox(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

        if not os.path.isdir('./screenshots'):
            os.mkdir('./screenshots')

        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
