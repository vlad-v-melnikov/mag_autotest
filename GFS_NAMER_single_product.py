import time
import random
import glob
import pyautogui
import logging
import os
import sys
from retry import retry

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from settings import Settings


def clear_screenshots():
    files = glob.glob('./screenshots/*.png')
    for f in files:
        os.unlink(f)


def log_config():
    logfile = "screenshot_maker.log"
    logging.root.handlers = [
        logging.FileHandler(filename=logfile, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )


class GFSScreenshotMaker:

    DEBUG = True
    DEBUG_PROD_NUM = 3
    IMAGE_DELAY = 2

    sites = {
        'test': "https://magtest.ncep.noaa.gov",
        'prod': "https://mag.ncep.noaa.gov",
    }

    handles = {}

    def __init__(self):
        self.settings = Settings()
        log_config()
        clear_screenshots()

        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(5)
        self.driver.maximize_window()

        # open sites
        try:
            self.open_test_site()
            self.open_prod_site()
        except TimeoutException as e:
            logging.error(f"Exception {type(e)} was thrown while trying to open TEST or PROD site")

        if not os.path.isdir('./screenshots'):
            os.mkdir('./screenshots')

    def __del__(self):
        self.tear_down()

    @retry(TimeoutException, tries=5, delay=1)
    def open_test_site(self):
        self.driver.get(self.sites['test'])
        self.handles['test'] = self.driver.window_handles[0]

    @retry(TimeoutException, tries=5, delay=1)
    def open_prod_site(self):
        self.driver.execute_script(f"window.open('https://mag.ncep.noaa.gov', 'new window')")
        self.handles['prod'] = self.driver.window_handles[1]

    @retry(TimeoutException, tries=5, delay=1)
    def click_back(self):
        self.driver.find_element_by_xpath("//button[contains(text(), 'Back')]").click()

    def switch_to_window(self, what_for: str):
        self.driver.switch_to.window(self.handles[what_for])

    def make_screenshot(self, hour, what_for, product):
        time.sleep(self.IMAGE_DELAY)  # let the image load
        screenshot_region = self.settings.SCREENSHOT_REGION
        region = screenshot_region
        pyautogui.screenshot('screenshots/' +
                             what_for + '_' +
                             product + '_' +
                             hour + '.png', region=region)

    def set_cycle_ids(self, what_for: str) -> None:
        if 'cycle' not in self.settings.links:
            self.driver.switch_to.window(self.handles[what_for])
            self.settings.links['cycle'] = \
                self.driver.find_element_by_xpath("//a[contains(@class, 'cycle_link')]").get_attribute('id')

    def set_product_ids(self, what_for: str) -> None:
        if 'products' not in self.settings.links:
            self.driver.switch_to.window(self.handles[what_for])
            self.settings.links['products'] = \
                [elem.get_attribute('id') for elem in
                 self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]

    def set_hour_ids(self, product, what_for) -> None:
        self.switch_to_window(what_for)
        self.driver.find_element_by_id(product).click()
        time.sleep(2)
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        sample = random.sample(range(len(elements)), self.settings.SAMPLE_SIZE)
        self.settings.links[product] = [elements[i].get_attribute('id') for i in sample]

    @retry(TimeoutException, tries=3, delay=2)
    def click_hour(self, hour, what_for: str):
        action = ActionChains(self.driver)
        if what_for == 'test':
            time.sleep(1)
        element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, hour)))
        action.move_to_element(element).perform()
        if what_for == 'test':
            time.sleep(2)
        element.click()

    def screenshot_one_hour(self, hour, what_for, product) -> None:
        try:
            self.click_hour(hour, what_for)
            self.make_screenshot(hour, what_for, product)
            self.click_back()
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking hour or "
                          f"clicking 'Back'")

    def click_product(self, what_for, product):
        self.switch_to_window(what_for)
        action = ActionChains(self.driver)
        element = self.driver.find_element_by_id(product)
        action.move_to_element(element).perform()
        if what_for == 'test':
            time.sleep(1)
        element.click()

    def iterate_one_product(self, product) -> None:
        for hour in self.settings.links[product]:
            for what_for in ('prod', 'test'):
                print(what_for, product, hour)
                try:
                    self.click_product(what_for, product)
                    self.screenshot_one_hour(hour, what_for, product)
                except Exception as e:
                    logging.error(
                        f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking product")

    def setup_page(self, handle) -> None:
        self.driver.switch_to.window(handle)
        self.driver.find_element_by_link_text(self.settings.links['section']).click()
        self.driver.find_element_by_link_text(self.settings.links['model']).click()
        self.driver.find_element_by_link_text(self.settings.links['area']).click()

    def iterate_products(self):
        product_counter = 0
        for product in self.settings.links['products']:
            product_counter += 1
            if self.DEBUG and product_counter > self.DEBUG_PROD_NUM:
                break

            self.set_hour_ids(product, 'prod')
            self.iterate_one_product(product)

    def test_gfs(self) -> None:
        for handle in self.handles.values():
            self.setup_page(handle)

        self.set_cycle_ids('test')
        self.set_product_ids('prod')

        for what_for, handle in self.handles.items():
            self.driver.switch_to.window(handle)
            self.driver.find_element_by_id(self.settings.links['cycle']).click()

        self.iterate_products()

    def tear_down(self):
        logging.info("Testing class destroyed. Windows closed.")
        for handle in self.handles.values():
            self.driver.switch_to.window(handle)
            self.driver.close()


def main():
    gfs_screenshot_maker = GFSScreenshotMaker()
    gfs_screenshot_maker.test_gfs()
    print("Testing complete")


if __name__ == "__main__":
    main()

# To Do:
# 0) Single driver, several windows
# 1) Multiple regions
