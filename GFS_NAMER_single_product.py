import time
import random
import glob
import pyautogui
import logging
import os
import sys

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    DEBUG_PROD_NUM = 5

    sites = {
        'test': "https://magtest.ncep.noaa.gov",
        'prod': "https://mag.ncep.noaa.gov",
    }

    drivers = {}

    def __init__(self):
        self.settings = Settings()

        for what_for in ('prod', 'test'):
            self.drivers[what_for] = webdriver.Chrome()
            self.drivers[what_for].maximize_window()
            self.drivers[what_for].get(self.sites[what_for])
            self.drivers[what_for].minimize_window()

        if not os.path.isdir('./screenshots'):
            os.mkdir('./screenshots')

        log_config()
        clear_screenshots()

    def click_back(self, purpose: str):
        self.drivers[purpose].find_element_by_xpath("//button[contains(text(), 'Back')]").click()

    def make_screenshot(self, hour, what_for, product):
        time.sleep(1)  # let the image load
        screenshot_region = self.settings.SCREENSHOT_REGION
        region = screenshot_region
        pyautogui.screenshot('screenshots/' +
                             what_for + '_' +
                             product + '_' +
                             hour + '.png', region=region)

    def set_cycle_ids(self, purpose: str) -> None:
        if 'cycle' not in self.settings.links:
            self.settings.links['cycle'] = \
                self.drivers[purpose].find_element_by_xpath("//a[contains(@class, 'cycle_link')]").get_attribute('id')

    def set_product_ids(self, purpose: str) -> None:
        if 'products' not in self.settings.links:
            self.settings.links['products'] = \
                [elem.get_attribute('id') for elem in
                 self.drivers[purpose].find_elements_by_xpath("//a[contains(@class, 'params_link')]")]

    def set_hour_ids(self, product, purpose) -> None:
        self.drivers[purpose].find_element_by_id(product).click()
        time.sleep(1)
        elements = self.drivers[purpose].find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        sample = random.sample(range(len(elements)), self.settings.SAMPLE_SIZE)
        self.settings.links[product] = [elements[i].get_attribute('id') for i in sample]

    def click_element(self, hour, purpose: str):
        element = WebDriverWait(self.drivers[purpose], 5).until(EC.presence_of_element_located((By.ID, hour)))
        element.click()

    def screenshot_one_hour(self, hour, what_for, product) -> None:
        try:
            self.click_element(hour, what_for)
            self.make_screenshot(hour, what_for, product)
            self.click_back(what_for)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product}")

    def iterate_one_product(self, product) -> None:
        for hour in self.settings.links[product]:
            for what_for in ('prod', 'test'):
                self.drivers[what_for].maximize_window()
                self.drivers[what_for].find_element_by_id(product).click()
                self.screenshot_one_hour(hour, what_for, product)
                self.drivers[what_for].minimize_window()

    def setup_page(self, what_for: str) -> None:
        self.drivers[what_for].maximize_window()
        self.drivers[what_for].find_element_by_link_text(self.settings.links['section']).click()
        self.drivers[what_for].find_element_by_link_text(self.settings.links['model']).click()
        self.drivers[what_for].find_element_by_link_text(self.settings.links['area']).click()
        self.drivers[what_for].minimize_window()

    def iterate_products(self):
        product_counter = 0
        for product in self.settings.links['products']:
            product_counter += 1
            if self.DEBUG and product_counter > self.DEBUG_PROD_NUM:
                break

            self.set_hour_ids(product, 'prod')
            self.iterate_one_product(product)

    def test_gfs(self) -> None:
        for what_for in self.drivers.keys():
            self.setup_page(what_for)

        self.set_cycle_ids('test')
        self.set_product_ids('prod')

        for what_for, driver in self.drivers.items():
            driver.find_element_by_id(self.settings.links['cycle']).click()

        self.iterate_products()

    def tear_down(self):
        logging.info("Testing complete")
        for driver in self.drivers.values():
            driver.close()


def main():
    gfs_screenshot_maker = GFSScreenshotMaker()
    gfs_screenshot_maker.test_gfs()
    gfs_screenshot_maker.tear_down()


if __name__ == "__main__":
    main()

# To Do:
# 1) Multiple regions
