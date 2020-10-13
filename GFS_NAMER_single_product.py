import unittest
import time
import random
import os
import glob
import pyautogui
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

    def setUp(self) -> None:
        super().setUp()
        self.settings = Settings()

    def _set_cycle_ids(self) -> None:
        if 'cycle' not in self.settings.links:
            self.settings.links['cycle'] = \
                self.driver.find_element_by_xpath("//a[contains(@class, 'cycle_link')]").get_attribute('id')

    def _set_product_ids(self) -> None:
        if 'products' not in self.settings.links:
            self.settings.links['products'] = \
                [elem.get_attribute('id') for elem in
                 self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]

    @retry((NoSuchElementException, StaleElementReferenceException), tries=3, delay=1)
    def click_hour(self, hour):
        self.driver.find_element_by_id(hour).click()

    def _test_one_product(self, ty, product) -> None:
        self.driver.find_element_by_id(product).click()
        time.sleep(1)
        if product not in self.settings.links:
            elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
            print(product, str(len(elements)))
            sample = random.sample(range(len(elements)), self.settings.SAMPLE_SIZE)
            self.settings.links[product] = [elements[i].get_attribute('id') for i in sample]
            print(self.settings.links[product])

        for hour in self.settings.links[product]:
            self.click_hour(hour)
            time.sleep(1)  # let the image load
            screenshot_region = self.settings.SCREENSHOT_REGION
            region = screenshot_region
            pyautogui.screenshot('screenshots/' +
                                 ty + '_' +
                                 product + '_' +
                                 hour + '.png', region=region)
            self.driver.find_element_by_class_name('nav_button').click()

    def test_GFS_NAMER_single_product(self) -> None:
        types = ['test', 'prod']
        sites = [
            "https://magtest.ncep.noaa.gov",
            "https://mag.ncep.noaa.gov",
        ]

        clear_screenshots()

        for ty, site in zip(types, sites):
            self.driver.get(site)

            # setting up the page
            self.driver.find_element_by_link_text(self.settings.links['section']).click()
            self.driver.find_element_by_link_text(self.settings.links['model']).click()
            self.driver.find_element_by_link_text(self.settings.links['area']).click()

            if ty == 'test':
                self._set_cycle_ids()
                self._set_product_ids()

            self.driver.find_element_by_id(self.settings.links['cycle']).click()

            # going over products
            for product in self.settings.links['products']:
                self._test_one_product(ty, product)

if __name__ == "__main__":
    unittest.main()
