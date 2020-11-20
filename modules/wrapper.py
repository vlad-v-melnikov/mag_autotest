import glob
import logging
import os
from retry import retry
from datetime import datetime
import sys
import time

# selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# internal
from modules.settings import Settings
import modules.dimensions as dim


def clear_screenshots(model=''):
    files = glob.glob(f'./screenshots/*{model}*.png')
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        print("Cleared previous screenshots for", model)
        logging.info("Cleared previous screenshots for" + model)


def log_config(log_name='screenshot_maker'):
    now = datetime.now()
    log_time = now.strftime("%Y%m%d%H%M%S")
    logging.basicConfig(filename=f'logs/{log_name}_{log_time}.log', format='%(asctime)s - %(levelname)s - %(message)s',
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

    def __init__(self,
                 model,
                 clear=True,
                 filename='json\settings_default.json',
                 headless=False,
                 log_name='screenshot_maker'):
        self.start_time = time.time()
        self.settings = Settings(filename)
        self.make_dirs_if_none(log_name)
        log_config(log_name)
        if model not in self.settings.plan.keys():
            print(f"Model name {model} not found. Exiting.")
            logging.info(f"Model name {model} not found. Exiting.")
            sys.exit(0)
        if self.settings.driver not in self.driver.keys():
            print("Unsupported web driver. Exiting.")
            logging.info("Unsupported web driver. Exiting.")
            sys.exit(0)

        if clear:
            clear_screenshots(model)

        print("Setting up web driver...", end=' ')
        logging.info("Setting up web driver...")
        options = self.driver_options[self.settings.driver]()
        if headless:
            self.settings.headless = headless
        options.headless = self.settings.headless
        if self.settings.driver == "Chrome":
            options.add_argument(f"--window-size={dim.WINDOW_WIDTH},{dim.WINDOW_HEIGHT_CHROME}")
        else:
            options.add_argument(f"--width={dim.WINDOW_WIDTH}")
            options.add_argument(f"--height={dim.WINDOW_HEIGHT_FIREFOX}")
        self.driver = self.driver[self.settings.driver](options=options)
        self.driver.set_page_load_timeout(5)

        if sys.platform == 'linux' and not self.settings.headless:
            new_height = dim.WINDOW_HEIGHT_FIREFOX if self.settings.driver == "Firefox" else dim.WINDOW_HEIGHT_CHROME
            self.driver.set_window_size(dim.WINDOW_WIDTH, new_height)
        if sys.platform != 'linux' and not self.settings.headless:
            self.driver.maximize_window()

        print("Done.")
        logging.info("Done.")

        try:
            self.open_test_site()
            self.open_prod_site()
        except TimeoutException as e:
            logging.error(f"Exception {type(e)} was thrown while trying to open TEST or PROD site")

    def make_dirs_if_none(self, log_name):
        if log_name == 'screenshot_maker' and not os.path.isdir('./screenshots'):
            print("Making directory for screenshots")
            logging.info("Making directory for screenshots")
            os.mkdir('./screenshots')
        if log_name == 'check_today' and not os.path.isdir('./reports'):
            print("Making directory for reports")
            logging.info("Making directory for reports")
            os.mkdir('./reports')
        if not os.path.isdir('./logs'):
            print("Making directory for logs")
            logging.info("Making directory for logs")
            os.mkdir('./logs')

    @retry(TimeoutException, tries=5, delay=1)
    def open_test_site(self):
        print(f"Opening test site {self.settings.sites['test']}...", end=' ')
        logging.info(f"Opening test site {self.settings.sites['test']}...")
        self.driver.get(self.settings.sites['test'])
        self.handles['test'] = self.driver.window_handles[0]
        print("Done.")
        logging.info("Done.")

    @retry(TimeoutException, tries=5, delay=1)
    def open_prod_site(self):
        print(f"Opening prod site {self.settings.sites['prod']}...", end=' ')
        logging.info(f"Opening prod site {self.settings.sites['prod']}...")
        self.driver.execute_script(f"window.open('{self.settings.sites['prod']}', 'new window')")
        self.handles['prod'] = self.driver.window_handles[1]
        print("Done.")
        logging.info("Done.")

    def tear_down(self):
        print("Closing sites...", end=' ')
        logging.info("Closing sites...")
        for handle in self.handles.values():
            self.driver.switch_to.window(handle)
            self.driver.close()
        print("Done.")
        logging.info("Done.")
        print(f"Screenshots taken. Running time: {(time.time() - self.start_time):.2f} seconds.")
        logging.info(f"Screenshots taken. Running time: {(time.time() - self.start_time):.2f} seconds.")
