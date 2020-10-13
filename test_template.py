import unittest
import os
from selenium import webdriver


class TestParent(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

        if not os.path.isdir('./screenshots'):
            os.mkdir('./screenshots')

        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
