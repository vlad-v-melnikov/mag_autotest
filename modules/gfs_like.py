import time
import random
import logging
from retry import retry
from datetime import date

# selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.webdriver.support.color import Color
from selenium.webdriver.support.ui import WebDriverWait

from modules.settings import Settings

class GfsLike:

    def __init__(self, model, driver, handles, filename='json\settings_default.json'):
        self.settings = Settings(filename)
        self.plan = self.settings.plan[model]
        self.driver = driver
        self.handles = handles
        self.counter = 0
        self.total = 0

    @retry(TimeoutException, tries=5, delay=1)
    def click_back(self):
        try:
            element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Back')]")))
            element.click()
        except Exception as e:
            logging.error(f"Exception {type(e)} while clicking 'Back' button")

    def switch_to_window(self, what_for: str):
        self.driver.switch_to.window(self.handles[what_for])

    def make_screenshot(self, **kwargs):
        area, hour, what_for, product = kwargs.values()
        time.sleep(self.settings.delays['image'])  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                     what_for + '_' +
                                     self.plan['model'] + '_' +
                                     area + '_' +
                                     product + '_' +
                                     hour + '.png')

    def set_area_ids(self) -> None:
        what_for = self.settings.sites['area_from']

        print(f"Setting areas for {self.plan['model']} from {what_for}...", end=' ')
        logging.info(f"Setting areas for {self.plan['model']} from {what_for}...")

        if 'area' in self.plan.keys() and len(self.plan['area']) > 0:
            print(f"{len(self.plan['area'])} areas prescribed in settings file. Done.")
            logging.info(f"{len(self.plan['area'])} areas prescribed in settings file. Done.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.click_model()
        elements = self.get_all_area_ids()
        assert len(elements) > 0, 'No areas found'

        if 'area_count' in self.plan.keys() and 0 < self.plan['area_count'] <= len(elements):
            elements = random.sample(elements, self.plan['area_count'])
        self.plan['area'] = {}
        for element in elements:
            area = self.process_area(element)
            self.plan['area'][area] = []

        print(f"{len(elements)} area(s) chosen.")
        logging.info(f"{len(elements)} area(s) chosen.")

    def process_area(self, element):
        return element.get_attribute('class')

    def get_all_area_ids(self):
        elements = self.driver.find_elements_by_xpath(
            "//a[contains(@id, 'modarea') and not(contains(@class, 'deselect'))]")
        return elements

    def set_cycle_id(self, area) -> None:
        print(f"Setting cycle for {area}...", end=' ')
        logging.info(f"Setting cycle for {area}...")
        if 'area_cycle' in self.plan.keys() \
                and area in self.plan['area_cycle'].keys():
            print("Set by prescribed cycle.")
            logging.info("Set by prescribed cycle.")
            return

        what_for = self.settings.sites['cycle_from']
        self.driver.switch_to.window(self.handles[what_for])
        self.reset_to_base(what_for)
        self.click_area(area)

        cycles = self.get_all_cycles(area)

        if 'area_cycle' not in self.plan.keys():
            self.plan['area_cycle'] = {}
        self.save_cycle_to_plan(area, cycles)

        print(f"Set cycle {self.plan['area_cycle'][area]} for area {area}.")
        logging.info(f"Set cycle {self.plan['area_cycle'][area]} for area {area}.")

    def save_cycle_to_plan(self, area, cycles):
        self.plan['area_cycle'][area] = cycles[1].get_attribute('id') if len(cycles) > 1 \
            else cycles[0].get_attribute('id')

    @retry(AssertionError, tries=3, delay=2)
    def get_all_cycles(self, area='', product=''):
        # cycle is previous to the last one except for single element. Has to contain today's date
        if self.settings.sites['today_only']:
            date_today = date.today().strftime("%Y%m%d")
            cycles = self.driver.find_elements_by_xpath(f"//a[contains(@class, 'cycle_link') "
                                                        f"and (contains(@id, {date_today}))]")
        else:
            cycles = self.driver.find_elements_by_xpath(f"//a[contains(@class, 'cycle_link')]")
        assert len(cycles) > 0, f'No cycles found {area}, {product}'
        return cycles

    def set_product_ids(self, area: str) -> None:
        what_for = self.settings.sites['products_from']

        print(f"Setting products for {area} from {what_for}...", end=' ')
        logging.info(f"Setting products for {area} from {what_for}...")

        if len(self.plan['area'][area]) > 0:
            print("Prescribed in settings.")
            logging.info("Prescribed in settings.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.reset_to_base(what_for)
        self.click_area(area)
        time.sleep(self.settings.delays['common'])
        elements = self.get_all_product_ids()
        assert len(elements) > 0, "Empty products"

        if 'product_count' in self.plan.keys() \
                and 0 < self.plan['product_count'] <= len(elements):
            elements = random.sample(elements, self.plan['product_count'])
        self.plan['area'][area] = elements
        print(f"{len(elements)} product(s) set.")
        logging.info(f"{len(elements)} product(s) set.")

    def get_all_product_ids(self):
        elements = [elem.get_attribute('id') for elem in
                    self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]
        return elements

    def set_hour_ids(self, area, product) -> None:
        self.click_product(product)
        self.click_cycle(area=area, product=product)
        time.sleep(self.settings.delays['common'])
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        if 'hour_count' in self.plan.keys() \
                and 0 < self.plan['hour_count'] <= len(elements):
            elements = random.sample(elements, self.plan['hour_count'])
        self.plan[(area, product)] = [element.get_attribute('id') for element in elements]

    @retry(TimeoutException, tries=3, delay=2)
    def click_hour(self, hour, force=False):
        try:
            self.hover_and_click(hour, force=force)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour} while clicking hour")

    def screenshot_one_hour(self, **kwargs) -> None:
        area, hour, what_for, product = kwargs.values()
        self.final_click(hour)
        self.make_screenshot(area=area, hour=hour, what_for=what_for, product=product)
        self.click_back()

    @retry(TimeoutException, tries=3, delay=2)
    def final_click(self, hour):
        self.click_hour(hour, force=True)
        self.wait_image_page_load()

    def wait_image_page_load(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), \"Page Help\")]")))

    def hover_and_click(self, identifier, type='id', force=False):
        if type == 'link_text':
            xpath_str = f"//a[contains(text(), \"{identifier}\")]"
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_str)))
        else:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, identifier)))

        color = Color.from_string(element.value_of_css_property('color')).hex
        if force or color == '#0000ff':  # blue, not selected
            action = ActionChains(self.driver)
            try:
                action.move_to_element(element).perform()
            except MoveTargetOutOfBoundsException as e:
                logging.error("Link to hover over is not in the screen. But I still can click it. Continuing.")
            time.sleep(self.settings.delays['hover_and_click'])
            element.click()
            time.sleep(self.settings.delays['hover_and_click'])

    def click_product(self, product):
        try:
            self.hover_and_click(product)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {product} while clicking product")

    def click_cycle(self, **kwargs):
        area = kwargs['area']
        cycle = self.plan['area_cycle'][area]
        try:
            self.hover_and_click(cycle)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {cycle} while clicking cycle")

    def click_model(self):
        try:
            self.hover_and_click('modtype_' + self.plan['model'])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking {self.plan['model']}")

    def click_area(self, area):
        try:
            self.hover_and_click('modarea_' + area)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking {area}")

    def iterate_one_product(self, what_for, area, product) -> None:
        for hour in self.plan[(area, product)]:
            self.print_info_string(what_for, area, self.plan['area_cycle'][area], product, hour)
            self.click_product(product)
            self.click_cycle(area=area, product=product)
            self.screenshot_one_hour(name=area, hour=hour, what_for=what_for, product=product)

    def print_info_string(self, *args):
        output = ' '.join(args)
        self.counter += 1
        info_str = f"{self.counter} out of {self.calc_total()}: " \
                   + f"Processing {output}... "
        print(info_str)
        logging.info(info_str)

    def setup_page(self, what_for) -> None:
        print(f"Setting up page for {what_for}...", end=' ')
        logging.info(f"Setting up page for {what_for}...")
        self.switch_to_window(what_for)
        self.reset_to_base(what_for)
        print("Done.")
        logging.info("Done.")

    def iterate_products(self, what_for, area):
        for product in self.plan['area'][area]:
            if (area, product) not in self.plan.keys():
                self.set_hour_ids(area, product)
            self.iterate_one_product(what_for, area, product)

    @retry(TimeoutException, tries=5, delay=2)
    def reset_to_base(self, what_for):
        section = self.plan['section'].lower().replace(' ', '%20')
        site = self.settings.sites[what_for]
        url = f"{site}/model-guidance-model-area.php?group={section}#"

        if url != self.driver.current_url:
            self.driver.get(url)
        self.click_model()

    def iterate_what_for_areas(self):
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            for area in self.plan['area'].keys():
                self.reset_to_base(what_for)
                self.click_area(area)
                self.iterate_products(what_for, area)

    def set_common_for_all_areas(self):
        self.set_area_ids()

    def set_for_each_area(self):
        counter = 0
        total = len(self.plan['area'].keys())
        for area in self.plan['area'].keys():
            counter += 1
            print(f"Area {counter} out of {total}:")
            logging.info(f"Area {counter} out of {total}:")
            self.set_product_ids(area)
            self.set_cycle_id(area)

    def make_now(self) -> None:
        for what_for in self.handles.keys():
            self.setup_page(what_for)

        self.set_common_for_all_areas()
        self.set_for_each_area()

        self.iterate_what_for_areas()
        print("Processing complete.")
        logging.info("Processing complete.")

    def calc_total(self):
        total_products = 0
        for area in self.plan['area']:
            total_products += len(self.plan['area'][area])
        hours = self.plan['hour_count']
        total = total_products * hours * self.get_site_count()
        return total

    def get_site_count(self):
        return len(self.settings.sites['order_of_iteration'])


if __name__ == "__main__":
    print("Not an application")
    exit(0)