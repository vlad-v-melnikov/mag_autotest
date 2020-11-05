import glob
import logging
import os
import sys
from retry import retry
from datetime import datetime
import sys

# selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# internal
from modules.settings import Settings


def clear_screenshots(model):
    files = glob.glob(f'./screenshots/*{model}*.png')
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        print("Cleared previous screenshots for", model)


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
    driver_options = {
        'Firefox': FirefoxOptions,
        'Chrome': ChromeOptions,
    }

    def __init__(self, model, clear=True, filename='settings_default.json', headless=False):
        self.settings = Settings(filename)
        if model not in self.settings.plan.keys():
            print(f"Model name {model} not found. Exiting.")
            sys.exit(0)
        if self.settings.driver not in self.driver.keys():
            print("Unsupported web driver. Exiting.")
            sys.exit(0)

        self.make_dirs_if_none()
        log_config()
        if clear:
            clear_screenshots(model)

        print("Setting up web driver...", end=' ')
        options = self.driver_options[self.settings.driver]()
        options.headless = self.settings.headless
        self.driver = self.driver[self.settings.driver](options=options)

        self.driver.set_page_load_timeout(5)
        self.driver.maximize_window()
        print("Done.")

        try:
            self.open_test_site()
            self.open_prod_site()
        except TimeoutException as e:
            logging.error(f"Exception {type(e)} was thrown while trying to open TEST or PROD site")

    def make_dirs_if_none(self):
        if not os.path.isdir('./screenshots'):
            print("Making directory for screenshots")
            os.mkdir('./screenshots')
        if not os.path.isdir('./logs'):
            print("Making directory for logs")
            os.mkdir('./logs')

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
