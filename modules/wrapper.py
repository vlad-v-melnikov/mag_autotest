import glob
import logging
import os
from retry import retry

# selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from datetime import datetime

# internal
from keep.settings_old import Settings


def clear_screenshots():
    files = glob.glob('./screenshots/*.png')
    for f in files:
        os.unlink(f)
    print("Cleared previous screenshots")


def log_config():
    now = datetime.now()
    log_time = now.strftime("%Y%m%d%H%M%S")
    logging.basicConfig(filename=f'logs\screenshot_maker_{log_time}.log', format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)


class Wrapper:
    handles = {}
    driver = {
        'Firefox': webdriver.Firefox,
        'Chrome': webdriver.Chrome,
    }

    def __init__(self):
        self.settings = Settings()
        log_config()
        clear_screenshots()

        print("Setting up web driver...", end=' ')
        self.driver = self.driver[self.settings.driver]()
        self.driver.set_page_load_timeout(5)
        self.driver.maximize_window()
        print("Done.")

        try:
            self.open_test_site()
            self.open_prod_site()
        except TimeoutException as e:
            logging.error(f"Exception {type(e)} was thrown while trying to open TEST or PROD site")

        if not os.path.isdir('../screenshots'):
            os.mkdir('../screenshots')

    @retry(TimeoutException, tries=5, delay=1)
    def open_test_site(self):
        print(f"Opening test site {self.settings.sites['test']}...", end=' ')
        self.driver.get(self.settings.sites['test'])
        self.handles['test'] = self.driver.window_handles[0]
        print("Done.")

    @retry(TimeoutException, tries=5, delay=1)
    def open_prod_site(self):
        print(f"Opening prod site {self.settings.sites['prod']}...", end=' ')
        self.driver.execute_script(f"window.open('{self.settings.sites['prod']}', 'new window')")
        self.handles['prod'] = self.driver.window_handles[1]
        print("Done.")

    def tear_down(self):
        print("Closing sites...", end=' ')
        for handle in self.handles.values():
            self.driver.switch_to.window(handle)
            self.driver.close()
        print("Done.")
