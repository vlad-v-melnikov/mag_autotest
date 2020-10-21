import time
import random
import glob
import pyautogui
import logging
import os
import sys
from retry import retry
from pprint import pprint

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from datetime import datetime

from settings import Settings


def clear_screenshots():
    files = glob.glob('./screenshots/*.png')
    for f in files:
        os.unlink(f)


def log_config():
    now = datetime.now()
    log_time = now.strftime("%Y%m%d%H%M%S")
    logging.basicConfig(filename=f'logs\screenshot_maker_{log_time}.log', format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)


class GFSScreenshotMaker:

    IMAGE_DELAY = 1

    handles = {}

    def __init__(self):
        self.settings = Settings()
        log_config()
        clear_screenshots()

        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(5)
        self.driver.maximize_window()

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
        self.driver.get(self.settings.sites['test'])
        self.handles['test'] = self.driver.window_handles[0]

    @retry(TimeoutException, tries=5, delay=1)
    def open_prod_site(self):
        self.driver.execute_script(f"window.open('{self.settings.sites['prod']}', 'new window')")
        self.handles['prod'] = self.driver.window_handles[1]

    @retry(TimeoutException, tries=5, delay=1)
    def click_back(self):
        element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Back')]")))
        element.click()

    def switch_to_window(self, what_for: str):
        self.driver.switch_to.window(self.handles[what_for])

    def make_screenshot(self, area, hour, what_for, product):
        time.sleep(self.IMAGE_DELAY)  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                     what_for + '_' +
                                     area + '_' +
                                     product + '_' +
                                     hour + '.png')

    def set_area_ids(self, what_for: str) -> None:
        if 'area' in self.settings.plan.keys() and len(self.settings.plan['area']) > 0:
            return

        print("Setting areas...")
        self.driver.switch_to.window(self.handles[what_for])
        element_id = 'modtype_' + self.settings.plan['model']
        self.driver.find_element_by_id(element_id).click()
        time.sleep(1)
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'modarea') and not(contains(@class, 'deselect'))]")
        if 'area_count' in self.settings.plan.keys() and self.settings.plan['area_count'] > 0:
            elements = random.sample(elements, self.settings.plan['area_count'])
        self.settings.plan['area'] = {}
        for element in elements:
            area_name = element.get_attribute('class')
            self.settings.plan['area'][area_name] = []
        print("Done.")

    def set_cycle_id(self, what_for: str) -> None:
        if 'cycle' in self.settings.plan.keys():
            return

        print("Setting cycle...")
        self.driver.switch_to.window(self.handles[what_for])
        # click on the model
        element_id = 'modtype_' + self.settings.plan['model']
        self.driver.find_element_by_id(element_id).click()
        # click on the area
        element_id = 'modarea_' + next(iter(self.settings.plan['area']))
        self.driver.find_element_by_id(element_id).click()
        time.sleep(1)
        self.settings.plan['cycle'] = \
            self.driver.find_element_by_xpath("//a[contains(@class, 'cycle_link')]").get_attribute('id')
        print("Done.")

    def set_product_ids(self, what_for: str, area_name: str) -> None:
        if len(self.settings.plan['area'][area_name]) > 0:
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.reset_to_area(what_for, area_name)
        self.driver.find_element_by_class_name(area_name).click()
        time.sleep(1)
        elements = [elem.get_attribute('id') for elem in self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]
        if 'product_count' in self.settings.plan.keys() and self.settings.plan['product_count'] > 0:
            elements = random.sample(elements, self.settings.plan['product_count'])
        self.settings.plan['area'][area_name] = elements

    def set_hour_ids(self, area_name, product) -> None:
        time.sleep(1)
        self.driver.find_element_by_id(product).click()
        time.sleep(2)
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        if 'hour_count' in self.settings.plan.keys() and self.settings.plan['hour_count'] > 0:
            elements = random.sample(elements, self.settings.plan['hour_count'])
        self.settings.plan[(area_name, product)] = [element.get_attribute('id') for element in elements]

    @retry(TimeoutException, tries=3, delay=2)
    def click_hour(self, hour, what_for: str):
        action = ActionChains(self.driver)
        time.sleep(1)
        element = self.driver.find_element_by_id(hour)
        action.move_to_element(element).perform()
        time.sleep(2)
        element.click()

    def screenshot_one_hour(self, area, hour, what_for, product) -> None:
        try:
            self.click_hour(hour, what_for)
            self.make_screenshot(area, hour, what_for, product)
            self.click_back()
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking hour or "
                          f"clicking 'Back'")

    def click_product(self, product):
        time.sleep(1)
        action = ActionChains(self.driver)
        element = self.driver.find_element_by_id(product)
        action.move_to_element(element).perform()
        time.sleep(1)
        element.click()

    def iterate_one_product(self, what_for, area_name, product) -> None:
        for hour in self.settings.plan[(area_name, product)]:
            print(f"Processing {what_for} {area_name} {product} {hour}... ", end='')
            try:
                self.click_product(product)
                print(f"Clicked {what_for} {area_name} {product} {hour}... ")
                self.screenshot_one_hour(area_name, hour, what_for, product)
            except Exception as e:
                logging.error(
                    f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking product")
            print("Done.")

    def setup_page(self, what_for) -> None:
        self.switch_to_window(what_for)
        self.reset_to_area(what_for)

    def iterate_products(self, what_for, area_name):
        for product in self.settings.plan['area'][area_name]:
            if (area_name, product) not in self.settings.plan.keys():
                self.set_hour_ids(area_name, product)
                print("Just set hour ids for", product)
            self.iterate_one_product(what_for, area_name, product)

    @retry(TimeoutException, tries=5, delay=2)
    def reset_to_area(self, what_for, area_name=''):
        section = self.settings.plan['section'].lower()
        model = self.settings.plan['model'].lower()
        site = self.settings.sites[what_for]
        url = f"{site}/model-guidance-model-area.php?group={section}&model={model}&area={area_name.lower()}"
        self.driver.get(url)

    def iterate_what_for_areas(self):
        for what_for in ('test', 'prod'):
            self.switch_to_window(what_for)
            for area_name in self.settings.plan['area'].keys():
                self.reset_to_area(what_for, area_name)
                self.driver.find_element_by_class_name(area_name).click()
                self.iterate_products(what_for, area_name)

    def test_gfs(self) -> None:
        for what_for in self.handles.keys():
            self.setup_page(what_for)

        self.set_area_ids('prod')
        self.set_cycle_id('test')

        print("Using cycle", self.settings.plan['cycle'])

        for area in self.settings.plan['area'].keys():
            self.set_product_ids('test', area)

        self.iterate_what_for_areas()

    def tear_down(self):
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
# 1) Sampler for areas V
# 2) Next area - actually, I simply need to change the settings file.
