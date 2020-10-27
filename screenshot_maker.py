import time
import random
import logging
from retry import retry
from datetime import date

# selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from settings import Settings

class ScreenshotMaker:

    IMAGE_DELAY = 1

    def __init__(self, model, driver, handles):
        self.settings = Settings()
        self.plan = self.settings.plan[model]
        self.driver = driver
        self.handles = handles

    @retry(TimeoutException, tries=5, delay=1)
    def click_back(self):
        element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Back')]")))
        element.click()

    def switch_to_window(self, what_for: str):
        self.driver.switch_to.window(self.handles[what_for])

    def make_screenshot(self, **kwargs):
        area, hour, what_for, product = kwargs.values()
        time.sleep(self.IMAGE_DELAY)  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                     what_for + '_' +
                                     self.plan['model'] + '_' +
                                     area + '_' +
                                     product + '_' +
                                     hour + '.png')

    def set_area_ids(self) -> None:
        what_for = self.settings.sites['area_from']
        if 'area' in self.plan.keys() and len(self.plan['area']) > 0:
            return

        print("Setting areas...")
        self.driver.switch_to.window(self.handles[what_for])
        element_id = 'modtype_' + self.plan['model']
        self.driver.find_element_by_id(element_id).click()
        time.sleep(1)
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'modarea') and not(contains(@class, 'deselect'))]")
        if 'area_count' in self.plan.keys() and 0 < self.plan['area_count'] <= len(elements):
            elements = random.sample(elements, self.plan['area_count'])
        self.plan['area'] = {}
        for element in elements:
            area_name = element.get_attribute('class')
            self.plan['area'][area_name] = []
        print("Done.")

    def set_cycle_id(self) -> None:
        what_for = self.settings.sites['cycle_from']
        if 'cycle' in self.plan.keys():
            return

        print("Setting cycle...")
        self.driver.switch_to.window(self.handles[what_for])
        # click on the model
        element_id = 'modtype_' + self.plan['model']
        self.driver.find_element_by_id(element_id).click()
        # click on the area
        element_id = 'modarea_' + next(iter(self.plan['area']))
        self.driver.find_element_by_id(element_id).click()
        time.sleep(1)
        # cycle is previous to the last one except for single element. Has to contain today's date
        date_today = date.today().strftime("%Y%m%d")
        cycles = self.driver.find_elements_by_xpath(f"//a[contains(@class, 'cycle_link') "
                                                    f"and (contains(@id, {date_today}))]")
        self.plan['cycle'] = cycles[1].get_attribute('id') if len(cycles) > 1 else cycles[0].get_attribute('id')
        print("Done.")

    def set_product_ids(self, what_for: str, area_name: str) -> None:
        if len(self.plan['area'][area_name]) > 0:
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.reset_to_area(what_for, area_name)
        self.driver.find_element_by_class_name(area_name).click()
        time.sleep(2)
        elements = [elem.get_attribute('id') for elem in self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]
        if 'product_count' in self.plan.keys() \
                and 0 < self.plan['product_count'] <= len(elements):
            elements = random.sample(elements, self.plan['product_count'])
        self.plan['area'][area_name] = elements

    def set_hour_ids(self, area_name, product) -> None:
        self.click_product(product)
        self.click_cycle()
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        if 'hour_count' in self.plan.keys() \
                and 0 < self.plan['hour_count'] <= len(elements):
            elements = random.sample(elements, self.plan['hour_count'])
        self.plan[(area_name, product)] = [element.get_attribute('id') for element in elements]

    @retry(TimeoutException, tries=3, delay=2)
    def click_hour(self, hour):
        action = ActionChains(self.driver)
        time.sleep(1)
        element = self.driver.find_element_by_id(hour)
        action.move_to_element(element).perform()
        time.sleep(1)
        element.click()

    def screenshot_one_hour(self, **kwargs) -> None:
        area, hour, what_for, product = kwargs.values()
        try:
            self.click_hour(hour, what_for)
            self.make_screenshot(area, hour, what_for, product)
            self.click_back()
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking hour or "
                          f"clicking 'Back'")

    def hover_and_click_id(self, id):
        time.sleep(1)
        action = ActionChains(self.driver)
        element = self.driver.find_element_by_id(id)
        action.move_to_element(element).perform()
        time.sleep(1)
        element.click()
        time.sleep(1)

    def click_product(self, product):
        self.hover_and_click_id(product)

    def click_cycle(self):
        self.hover_and_click_id(self.plan['cycle'])

    def iterate_one_product(self, what_for, area_name, product, hours_just_set) -> None:
        for hour in self.plan[(area_name, product)]:
            print(f"Processing {what_for} {area_name} {product} {hour}... ", end='')
            try:
                if not hours_just_set:
                    self.click_product(product)
                    self.click_cycle()
                print(f"Clicked {what_for} {area_name} {product} {hour} for cycle {self.plan['cycle']}... ")
                self.screenshot_one_hour(name=area_name, hour=hour, what_for=what_for, product=product)
            except Exception as e:
                logging.error(
                    f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking product")
            print("Done.")

    def setup_page(self, what_for) -> None:
        self.switch_to_window(what_for)
        self.reset_to_area(what_for)

    def iterate_products(self, what_for, area_name):
        hours_just_set = False
        for product in self.plan['area'][area_name]:
            if (area_name, product) not in self.plan.keys():
                self.set_hour_ids(area_name, product)
                hours_just_set = True
            self.iterate_one_product(what_for, area_name, product, hours_just_set)

    @retry(TimeoutException, tries=5, delay=2)
    def reset_to_area(self, what_for, area_name=''):
        section = self.plan['section'].lower().replace(' ', '%20')
        model = self.plan['model'].lower()
        site = self.settings.sites[what_for]
        url = f"{site}/model-guidance-model-area.php?group={section}&model={model}&area={area_name.lower()}"
        self.driver.get(url)

    def iterate_what_for_areas(self):
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            for area_name in self.plan['area'].keys():
                self.reset_to_area(what_for, area_name)
                self.driver.find_element_by_class_name(area_name).click()
                self.iterate_products(what_for, area_name)

    def make_now(self) -> None:
        for what_for in self.handles.keys():
            self.setup_page(what_for)

        self.set_area_ids()
        self.set_cycle_id()
        print("Using cycle", self.plan['cycle'])

        for area in self.plan['area'].keys():
            self.set_product_ids(self.settings.sites['products_from'], area)

        self.iterate_what_for_areas()

if __name__ == "__main__":
    print("Not an application")
    exit(0)