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
    DEBUG_AREA_NUM = 2
    DEBUG_PROD_NUM = 2
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
        element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Back')]")))
        element.click()

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

    def set_area_ids(self, what_for: str) -> None:
        if 'area' not in self.settings.plan.keys():
            self.driver.switch_to.window(self.handles[what_for])
            elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'modarea') and not(contains(@class, 'deselect'))]")
            self.settings.plan['area'] = {}
            for element in elements:
                area_name = element.get_attribute('class')
                self.settings.plan['area'][area_name] = []

    def set_cycle_id(self, what_for: str) -> None:
        if 'cycle' in self.settings.plan.keys():
            return

        self.driver.switch_to.window(self.handles[what_for])
        element_id = next(iter(self.settings.plan['area']))
        self.driver.find_element_by_class_name(element_id).click()
        self.settings.plan['cycle'] = \
            self.driver.find_element_by_xpath("//a[contains(@class, 'cycle_link')]").get_attribute('id')

    def set_product_ids(self, what_for: str, area_name: str) -> None:
        if len(self.settings.plan['area'][area_name]) > 0:
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.driver.find_element_by_class_name(area_name).click()
        elements = [elem.get_attribute('id') for elem in self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]
        self.settings.plan['area'][area_name] = elements

    def set_hour_ids(self, area_name, product, what_for) -> None:
        self.switch_to_window(what_for)
        self.driver.find_element_by_id(product).click()
        time.sleep(2)
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        sample = random.sample(range(len(elements)), self.settings.HOUR_SAMPLE_SIZE)
        self.settings.plan[(area_name, product)] = [elements[i].get_attribute('id') for i in sample]
        print(area_name, product)
        pprint(self.settings.plan[(area_name, product)])

    @retry(TimeoutException, tries=3, delay=2)
    def click_hour(self, hour, what_for: str):
        action = ActionChains(self.driver)
        time.sleep(1)
        element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, hour)))
        action.move_to_element(element).perform()
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
        time.sleep(1)
        element.click()

    def iterate_one_product(self, area_name, product) -> None:
        for hour in self.settings.plan[(area_name, product)]:
            for what_for in ('prod', 'test'):
                print(what_for, area_name, product, hour)
                try:
                    self.click_product(what_for, product)
                    self.screenshot_one_hour(hour, what_for, product)
                except Exception as e:
                    logging.error(
                        f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking product")

    def setup_page(self, what_for) -> None:
        self.switch_to_window(what_for)
        self.reset_to_area(what_for)

    def iterate_products(self, area_name):
        for product in self.settings.plan['area'][area_name]:
            self.set_hour_ids(area_name, product, 'prod')
            self.iterate_one_product(area_name, product)

    @retry(TimeoutException, tries=5, delay=1)
    def reset_to_area(self, what_for, area_name=''):
        section = self.settings.plan['section'].lower()
        model = self.settings.plan['model'].lower()
        site = self.sites[what_for]
        url = f"{site}/model-guidance-model-area.php?group={section}&model={model}&area={area_name.lower()}"
        self.driver.get(url)

    def iterate_areas(self):
        for area_name in self.settings.plan['area'].keys():
            self.switch_to_window('test')
            self.reset_to_area('test', area_name)
            self.driver.find_element_by_class_name(area_name).click()
            self.switch_to_window('prod')
            self.reset_to_area('prod', area_name)
            self.driver.find_element_by_class_name(area_name).click()

            self.iterate_products(area_name)

    def test_gfs(self) -> None:
        for what_for in self.handles.keys():
            self.setup_page(what_for)

        # 1
        self.set_area_ids('prod')

        # 2
        self.set_cycle_id('test')

        # 3
        for area in self.settings.plan['area'].keys():
            self.set_product_ids('prod', area)

        self.iterate_areas()

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
