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
from selenium.webdriver.support.color import Color

from settings import Settings

class GfsLike:

    IMAGE_DELAY = 2

    def __init__(self, model, driver, handles):
        self.settings = Settings()
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
        time.sleep(self.IMAGE_DELAY)  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                     what_for + '_' +
                                     self.plan['model'] + '_' +
                                     area + '_' +
                                     product + '_' +
                                     hour + '.png')

    def set_area_ids(self) -> None:
        what_for = self.settings.sites['area_from']

        print(f"Setting areas for {self.plan['model']} from {what_for}...", end=' ')

        if 'area' in self.plan.keys() and len(self.plan['area']) > 0:
            print(f"{len(self.plan['area'])} areas prescribed in settings file. Done.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.click_model()
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'modarea') and not(contains(@class, 'deselect'))]")
        assert len(elements) > 0, 'No areas found'

        if 'area_count' in self.plan.keys() and 0 < self.plan['area_count'] <= len(elements):
            elements = random.sample(elements, self.plan['area_count'])
        self.plan['area'] = {}
        for element in elements:
            area = element.get_attribute('class')
            self.plan['area'][area] = []

        print(f"{len(elements)} areas chosen randomly.")

    def set_cycle_id(self, area) -> None:
        print(f"Setting cycle for {area}...", end=' ')
        if 'area_cycle' in self.plan.keys() \
                and area in self.plan['area_cycle'].keys():
            print("Set by prescribed cycle.")
            return

        what_for = self.settings.sites['cycle_from']
        self.driver.switch_to.window(self.handles[what_for])
        self.reset_to_base(what_for)
        self.click_area(area)
        time.sleep(1)

        cycles = self.get_all_cycles()

        if 'area_cycle' not in self.plan.keys():
            self.plan['area_cycle'] = {}
        self.plan['area_cycle'][area] = cycles[1].get_attribute('id') if len(cycles) > 1 \
            else cycles[0].get_attribute('id')

        print(f"Set cycle {self.plan['area_cycle'][area]} for area {area}.")

    @retry(AssertionError, tries=3, delay=1)
    def get_all_cycles(self):
        # cycle is previous to the last one except for single element. Has to contain today's date
        if self.settings.sites['today_only']:
            date_today = date.today().strftime("%Y%m%d")
            cycles = self.driver.find_elements_by_xpath(f"//a[contains(@class, 'cycle_link') "
                                                        f"and (contains(@id, {date_today}))]")
        else:
            cycles = self.driver.find_elements_by_xpath(f"//a[contains(@class, 'cycle_link')]")
        assert len(cycles) > 0, 'No cycles found'
        return cycles

    def set_product_ids(self, area: str) -> None:
        what_for = self.settings.sites['products_from']

        print(f"Setting products for {area} from {what_for}...", end=' ')

        if len(self.plan['area'][area]) > 0:
            print("Prescribed in settings.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        self.reset_to_base(what_for)
        self.click_area(area)
        time.sleep(1)

        elements = [elem.get_attribute('id') for elem in self.driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]

        assert len(elements) > 0, "Empty products"

        if 'product_count' in self.plan.keys() \
                and 0 < self.plan['product_count'] <= len(elements):
            elements = random.sample(elements, self.plan['product_count'])
        self.plan['area'][area] = elements
        print(f"{len(elements)} products set randomly.")

    def set_hour_ids(self, area, product) -> None:
        self.click_product(product)
        self.click_cycle(area=area, product=product)
        time.sleep(1)
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        if 'hour_count' in self.plan.keys() \
                and 0 < self.plan['hour_count'] <= len(elements):
            elements = random.sample(elements, self.plan['hour_count'])
        self.plan[(area, product)] = [element.get_attribute('id') for element in elements]

    @retry(TimeoutException, tries=3, delay=2)
    def click_hour(self, hour):
        time.sleep(1.5)
        try:
            self.hover_and_click(hour)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour} while clicking hour")

    def screenshot_one_hour(self, **kwargs) -> None:
        area, hour, what_for, product = kwargs.values()
        self.click_hour(hour)
        self.make_screenshot(area=area, hour=hour, what_for=what_for, product=product)
        self.click_back()

    def hover_and_click(self, identifier, type='id'):
        type_mapper = {
            'id': self.driver.find_element_by_id,
            'link_text': self.driver.find_element_by_link_text
        }

        element = type_mapper[type](identifier)
        color = Color.from_string(element.value_of_css_property('color')).hex
        if color == '#0000ff':  # blue, not selected
            action = ActionChains(self.driver)
            action.move_to_element(element).perform()
            time.sleep(1)
            element.click()
            time.sleep(1)

    def click_product(self, product):
        try:
            self.hover_and_click(product)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {product} while clicking product")

    def click_cycle(self, **kwargs):
        area = kwargs['area']
        time.sleep(1)
        cycle = self.plan['area_cycle'][area]
        try:
            self.hover_and_click(cycle)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {cycle} while clicking cycle")
        time.sleep(1)

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

    def iterate_one_product(self, what_for, area, product, hours_just_set) -> None:
        for hour in self.plan[(area, product)]:
            self.print_info_string(what_for, area, self.plan[('cycle', area, product)], product, hour)
            if not hours_just_set:
                self.click_product(product)
                self.click_cycle(area=area, product=product)
            self.screenshot_one_hour(name=area, hour=hour, what_for=what_for, product=product)

    def print_info_string(self, *args):
        output = ' '.join(args)
        self.counter += 1
        info_str = f"{self.counter} out of {self.calc_total()}: " \
                   + f"Processing {output}... "
        print(info_str, end=(' ' * 20))
        if self.counter < self.calc_total():
            print('\r', end='')
        else:
            print('\n', end='')

    def setup_page(self, what_for) -> None:
        print(f"Setting up page for {what_for}...", end=' ')
        self.switch_to_window(what_for)
        self.reset_to_base(what_for)
        print("Done.")

    def iterate_products(self, what_for, area):
        hours_just_set = False
        for product in self.plan['area'][area]:
            if (area, product) not in self.plan.keys():
                self.set_hour_ids(area, product)
                hours_just_set = True
            self.iterate_one_product(what_for, area, product, hours_just_set)

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
        for area in self.plan['area'].keys():
            self.set_product_ids(area)
            self.set_cycle_id(area)

    def make_now(self) -> None:
        for what_for in self.handles.keys():
            self.setup_page(what_for)

        self.set_common_for_all_areas()
        self.set_for_each_area()

        self.iterate_what_for_areas()
        print("Processing complete.")

    def calc_total(self):
        total_products = 0
        for area in self.plan['area']:
            total_products += len(self.plan['area'][area])
        first_area = next(iter(self.plan['area']))
        first_product = self.plan['area'][first_area][0]
        hours = len(self.plan[(first_area, first_product)])
        total = total_products * hours * 2
        return total


if __name__ == "__main__":
    print("Not an application")
    exit(0)