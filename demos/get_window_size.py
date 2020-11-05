from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
from retry import retry


class Main:

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.site = "https://magtest.ncep.noaa.gov"
        self.driver.set_page_load_timeout(5)
        try:
            self.open_site()
            self.open_site2()
        except TimeoutException as e:
            self.driver.close()

    @retry(TimeoutException, tries=5, delay=1)
    def open_site(self):
        self.driver.get(self.site)
        self.driver.maximize_window()

    @retry(TimeoutException, tries=5, delay=1)
    def open_site2(self):
        self.driver.execute_script("window.open('http://www.twitter.com', 'new window')")

    def close_all(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.close()


if __name__ == '__main__':
    main = Main()
    print(main.driver.get_window_size())
    main.close_all()

