import unittest
import time
import random
import os
import glob
import pyautogui
import logging
from test_template import TestParent
from settings import Settings
from pprint import pprint
from retry import retry
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException


def clear_screenshots():
    files = glob.glob('./screenshots/*.png')
    for f in files:
        os.unlink(f)


class MagTestTester(TestParent):

    DEBUG = True
    DEBUG_PROD_NUM = 5

    sites = {
        'test': "https://magtest.ncep.noaa.gov",
        'prod': "https://mag.ncep.noaa.gov",
    }

    def setUp(self) -> None:
        super().setUp()
        logging.basicConfig(filename='screenshot_maker.log', format='%(asctime)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.settings = Settings()
        clear_screenshots()

    def click_back(self):
        self.driver.find_element_by_xpath("//button[contains(text(), 'Back')]").click()

    def make_screenshot(self, hour, what_for, product):
        time.sleep(1)  # let the image load
        screenshot_region = self.settings.SCREENSHOT_REGION
        region = screenshot_region
        pyautogui.screenshot('screenshots/' +
                             what_for + '_' +
                             product + '_' +
                             hour + '.png', region=region)

    def set_cycle_ids(self) -> None:
        if 'cycle' not in self.settings.links:
            self.settings.links['cycle'] = \
                self.driver.find_element_by_xpath("//a[contains(@class, 'cycle_link')]").get_attribute('id')

    def set_product_ids(self) -> None:
        if 'products' not in self.settings.links:
            self.settings.links['products'] = \
                [elem.get_attribute('id') for elem in
                 self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]

    def set_hour_ids(self, product) -> None:
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        sample = random.sample(range(len(elements)), self.settings.SAMPLE_SIZE)
        self.settings.links[product] = [elements[i].get_attribute('id') for i in sample]

    def test_one_hour(self, hour, what_for, product) -> None:
        try:
            self.driver.find_element_by_id(hour).click()
            self.make_screenshot(hour, what_for, product)
            self.click_back()
        except Exception as e:
            logging.error(f"Exception was thrown for {hour}, {what_for}, {product}, {e}")

    def test_one_product(self, what_for, product) -> None:
        self.driver.find_element_by_id(product).click()
        time.sleep(1)
        if product not in self.settings.links:
            self.set_hour_ids(product)

        for hour in self.settings.links[product]:
            self.test_one_hour(hour, what_for, product)

    def setup_page(self) -> None:
        self.driver.find_element_by_link_text(self.settings.links['section']).click()
        self.driver.find_element_by_link_text(self.settings.links['model']).click()
        self.driver.find_element_by_link_text(self.settings.links['area']).click()

    def test_GFS_NAMER_single_product(self) -> None:
        for what_for, site in self.sites.items():
            self.driver.get(site)
            self.setup_page()

            if what_for == 'test':
                self.set_cycle_ids()
                self.set_product_ids()

            self.driver.find_element_by_id(self.settings.links['cycle']).click()

            product_counter = 0
            for product in self.settings.links['products']:
                product_counter += 1
                if self.DEBUG and product_counter > self.DEBUG_PROD_NUM:
                    break
                self.test_one_product(what_for, product)


if __name__ == "__main__":
    unittest.main()

# To Do: