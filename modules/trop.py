from modules.gfs_like import GfsLike
from retry import retry
from selenium.common.exceptions import TimeoutException
import logging
import random
import time
from pprint import pprint


class Trop(GfsLike):

    @retry(TimeoutException, tries=5, delay=2)
    def reset_to_base(self, what_for):
        section = self.plan['section'].lower().replace(' ', '%20')
        site = self.settings.sites[what_for]
        url = f"{site}/tropical-guidance-model-storm.php?group={section}#"

        if url != self.driver.current_url:
            self.driver.get(url)

    def set_storms(self):
        what_for = self.settings.sites['storms_from']

        print(f"Setting storms for {self.plan['model']} from {what_for}...", end=' ')
        logging.info(f"Setting storms for {self.plan['model']} from {what_for}...")

        if 'storm' in self.plan.keys() and len(self.plan['storm']) > 0:
            print(f"{len(self.plan['storm'])} storm(s) prescribed in settings file. Done.")
            logging.info(f"{len(self.plan['storm'])} storm(s) prescribed in settings file. Done.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        elements = self.get_all_storms()
        assert len(elements) > 0, 'No storms found'

        if 'storm_count' in self.plan.keys() and 0 < self.plan['storm_count'] <= len(elements):
            elements = random.sample(elements, self.plan['storm_count'])
        self.plan['storm'] = {}
        for element in elements:
            storm = element.text
            self.plan['storm'][storm] = {
                "types": [],
                "products": []
            }

        print(f"{len(elements)} storm(s) set.")
        logging.info(f"{len(elements)} storm(s) set.")

    def get_all_storms(self):
        elements = self.driver.find_elements_by_xpath(
            "//a[contains(@id, \"modstorm\")]")
        return elements

    def set_types(self, storm):
        what_for = self.settings.sites['storms_from']

        print(f"Setting types for {self.plan['model']} {storm} from {what_for}...", end=' ')
        logging.info(f"Setting types for {self.plan['model']} {storm} from {what_for}...")

        if 'types' in self.plan['storm'].keys() and len(self.plan['storm'][storm]['types']) > 0:
            print(f"{len(self.plan['storm']['types'])} type(s) prescribed in settings file. Done.")
            logging.info(f"{len(self.plan['storm']['types'])} types(s) prescribed in settings file. Done.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        elements = self.get_all_types()
        assert len(elements) > 0, 'No types found'

        if 'type_count' in self.plan.keys() and 0 < self.plan['type_count'] <= len(elements):
            elements = random.sample(elements, self.plan['type_count'])
        for element in elements:
            type = element.text
            self.plan['storm'][storm]['types'].append(type)

        print(f"{len(elements)} type(s) set.")
        logging.info(f"{len(elements)} type(s) set.")

    def set_cycle_trop(self):
        print(f"Setting cycle...", end=' ')
        logging.info(f"Setting cycle...")

        what_for = self.settings.sites['cycle_from']
        self.driver.switch_to.window(self.handles[what_for])

        cycles = self.get_all_cycles()
        self.plan['cycle'] = cycles[1].get_attribute('id') if len(cycles) > 1 else cycles[0].get_attribute('id')

        print(f"Set cycle {self.plan['cycle']}.")
        logging.info(f"Set cycle {self.plan['cycle']}.")

    def set_products_trop(self):
        print(f"Setting products...", end=' ')
        logging.info(f"Setting products from...")

        what_for = self.settings.sites['products_from']
        self.driver.switch_to.window(self.handles[what_for])
        self.click_cycle_trop()

        first_storm = next(iter(self.plan['storm'].keys()))
        if len(self.plan['storm'][first_storm]['products']) > 0:
            print("Prescribed in settings.")
            logging.info("Prescribed in settings.")
            return

        elements = self.get_all_product_ids()
        assert len(elements) > 0, "Empty products"

        if 'product_count' in self.plan.keys() \
                and 0 < self.plan['product_count'] <= len(elements):
            elements = random.sample(elements, self.plan['product_count'])
        for storm in self.plan['storm'].keys():
            self.plan['storm'][storm]['products'] = elements
        print(f"{len(elements)} product(s) set.")
        logging.info(f"{len(elements)} product(s) set.")

    def set_hours_trop(self):
        self.click_product(self.get_first_product())
        time.sleep(self.settings.delays['common'])

        elements = self.driver.find_elements_by_xpath("//a[contains(@href, 'goToTropicalImage')]")
        assert len(elements) > 0, 'Hours are empty'

        if 'hour_count' in self.plan.keys() \
                and 0 < self.plan['hour_count'] <= len(elements):
            elements = random.sample(elements, self.plan['hour_count'])
        hour_ids = [element.text for element in elements]
        for storm in self.plan['storm'].keys():
            self.plan['storm'][storm]['hours'] = hour_ids

    def get_all_types(self):
        elements = self.driver.find_elements_by_xpath(
            "//a[contains(@id, \"modtype\") and not(contains(@class, \"deselect\"))]")
        return elements

    def click_storm(self, storm):
        try:
            self.hover_and_click('modstorm_' + storm)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking {storm}")

    def click_type(self, type):
        try:
            self.hover_and_click('modtype_' + type)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking {type}")

    def click_cycle_trop(self):
        try:
            self.hover_and_click(self.plan['cycle'])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking cycle {self.plan['cycle']}")

    def go_one_level_down(self):
        first_storm = next(iter(self.plan['storm'].keys()))
        first_type = self.plan['storm'][first_storm]['types'][0]
        for handle in self.handles.values():
            self.driver.switch_to.window(handle)
            self.click_storm(first_storm)
            self.click_type(first_type)

    def get_first_product(self):
        first_storm = next(iter(self.plan['storm'].keys()))
        return self.plan['storm'][first_storm]['products'][0]

    def set_common_for_all(self):
        self.set_storms()
        for storm in self.plan['storm'].keys():
            self.click_storm(storm)
            self.set_types(storm)

        self.go_one_level_down()

        self.set_cycle_trop()
        self.set_products_trop()
        self.set_hours_trop()

    def set_for_each(self):
        pass

    def iterate_types(self, what_for, storm):
        for type in self.plan['storm'][storm]['types']:
            self.click_type(type)
            self.iterate_one_type(what_for, storm, type)
            self.click_back()

    def click_hour(self, hour, force=False):
        try:
            self.hover_and_click(hour, type='link_text')
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour} while clicking hour")

    def iterate_one_type(self, what_for, storm, type):
        self.click_cycle_trop()
        for product in self.plan['storm'][storm]['products']:
            self.click_product(product)
            for hour in self.plan['storm'][storm]['hours']:
                self.print_info_string(what_for, storm, type, product, hour)
                self.click_hour(hour)
                self.screenshot_one_hour(name=f'{storm}_{type}', hour=hour, what_for=what_for, product=product)

    def screenshot_one_hour(self, **kwargs) -> None:
        name, hour, what_for, product = kwargs.values()
        self.make_screenshot(area=name, hour=hour, what_for=what_for, product=product)
        self.click_back()

    def calc_total(self):
        for_all_storms = 0
        for storm in self.plan['storm'].keys():
            types_no = len(self.plan['storm'][storm]['types'])
            prod_no = len(self.plan['storm'][storm]['products'])
            hours_no = len(self.plan['storm'][storm]['hours'])
            for_all_storms += types_no * prod_no * hours_no
        return self.get_site_count() * for_all_storms

    def iterate_what_for(self):
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            for storm in self.plan['storm'].keys():
                self.reset_to_base(what_for)
                self.click_storm(storm)
                self.iterate_types(what_for, storm)
