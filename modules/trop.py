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
        what_for = self.settings.sites['products_from']

        print(f"Setting products from {what_for}...", end=' ')
        logging.info(f"Setting products from {what_for}...")

        #TO DO - continue tomorrow morning from here. Set same products for all storms
        first_storm = next(iter(self.plan['storm'].keys()))
        if len(self.plan['storm'][first_storm]) > 0:
            print("Prescribed in settings.")
            logging.info("Prescribed in settings.")
            return

        self.driver.switch_to.window(self.handles[what_for])

        elements = self.get_all_product_ids()
        assert len(elements) > 0, "Empty products"

        if 'product_count' in self.plan.keys() \
                and 0 < self.plan['product_count'] <= len(elements):
            elements = random.sample(elements, self.plan['product_count'])
        for storm in self.plan['storm'].keys():
            self.plan['storm'][storm]['products'] = elements
        print(f"{len(elements)} product(s) set.")
        logging.info(f"{len(elements)} product(s) set.")

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
        self.click_storm(first_storm)
        first_type = self.plan['storm'][first_storm]['types'][0]
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
        self.click_cycle_trop()
        self.set_products_trop()
        self.click_product(self.get_first_product())
        # self.set_product_ids()
        # self.set_hour_ids()

        pprint(self.plan['storm'])
        time.sleep(10)

    def set_for_each(self):
        pass

    def iterate_what_for(self):
        return
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            for area in self.plan['area'].keys():
                self.reset_to_base(what_for)
                self.click_area(area)
                self.iterate_products(what_for, area)
