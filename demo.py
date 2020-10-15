from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import copy
from settings import Settings
from pprint import pprint
import time
from retry import retry


class Main:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.site = "https://magtest.ncep.noaa.gov"
        self.driver.set_page_load_timeout(5)
        try:
            self.open_site()
        except TimeoutException as e:
            self.driver.close()

    @retry(TimeoutException, tries=5, delay=1)
    def open_site(self):
        self.driver.get(self.site)


if __name__ == '__main__':
    main = Main()
    main.driver.close()
