from modules.gfs_like import GfsLike
from retry import retry
from pprint import pprint
import logging
import random
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Soundings(GfsLike):
    @retry(TimeoutException, tries=5, delay=2)
    def reset_to_base(self, what_for):
        site = self.settings.sites[what_for]
        url = f"{site}/sounding-model-area.php"

        if url != self.driver.current_url:
            self.driver.get(url)

    def get_all_types(self):
        elements = self.driver.find_elements_by_xpath(
            "//div[contains(@id, \"model_id\")]")
        return elements

    def set_types(self) -> None:
        what_for = self.settings.sites['area_from']

        print(f"Setting types for {self.plan['model']} from {what_for}...", end=' ')
        logging.info(f"Setting types for {self.plan['model']} from {what_for}...")

        if 'type' in self.plan.keys() and len(self.plan['type']) > 0:
            print(f"{len(self.plan['type'])} model type(s) prescribed in settings file. Done.")
            logging.info(f"{len(self.plan['type'])} model type(s) prescribed in settings file. Done.")
            return

        self.driver.switch_to.window(self.handles[what_for])
        elements = self.get_all_types()
        assert len(elements) > 0, 'No types found'

        if 'type_count' in self.plan.keys() and 0 < self.plan['type_count'] <= len(elements):
            elements = random.sample(elements, self.plan['type_count'])
        self.plan['type'] = {}
        for element in elements:
            type_name = element.text
            self.plan['type'][type_name] = []

        print(f"{len(elements)} type(s) chosen.")
        logging.info(f"{len(elements)} type(s) chosen.")

    def click_tab(self):
        xpath_str = "//div[contains(text(), \"Stations Table\")]"
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_str)))
        element.click()

    def click_type(self):
        iden = self.plan['model'].lower() + '_model_id'
        self.hover_and_click(iden, force=True)

    def click_station(self, station):
        xpath_str = f"//span[contains(text(), \"{station}\")]"
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_str)))
        element.click()

    def get_all_stations(self):
        elements = self.driver.find_elements_by_xpath(
            "//span[contains(@class, \"namer_table_a\")]")
        elements[:] = [element.text for element in elements]
        return elements

    def set_stations(self):
        what_for = self.settings.sites['stations_from']
        self.driver.switch_to.window(self.handles[what_for])
        self.click_type()

        self.click_tab()
        print(f"Setting stations from {what_for}...", end=' ')
        logging.info(f"Setting stations from {what_for}...")

        if 'stations' in self.plan.keys() and len(self.plan['stations']) > 0:
            print("Prescribed in settings.")
            logging.info("Prescribed in settings.")
            return

        elements = self.get_all_stations()
        assert len(elements) > 0, "Empty stations"

        if 'station_count' in self.plan.keys() \
                and 0 < self.plan['station_count'] <= len(elements):
            elements = random.sample(elements, self.plan['station_count'])
        self.plan['stations'] = elements
        print(f"{len(elements)} station(s) set.")
        logging.info(f"{len(elements)} station(s) set.")

    def set_cycle_snd(self):
        print(f"Setting cycle...", end=' ')
        logging.info(f"Setting cycle...")

        cycles = self.get_all_cycles()
        self.plan['cycle'] = cycles[1].get_attribute('id') if len(cycles) > 1 \
            else cycles[0].get_attribute('id')

        print(f"Set cycle {self.plan['cycle']}.")
        logging.info(f"Set cycle {self.plan['cycle']}.")

    def click_cycle_snd(self):
        try:
            self.hover_and_click(self.plan['cycle'])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {self.plan['cycle']} while clicking cycle")

    def set_hours_snd(self):
        self.click_cycle_snd()
        time.sleep(self.settings.delays['common'])
        elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
        if 'hour_count' in self.plan.keys() \
                and 0 < self.plan['hour_count'] <= len(elements):
            elements = random.sample(elements, self.plan['hour_count'])
        self.plan['hours'] = [element.get_attribute('id') for element in elements]

    def set_common_for_all(self):
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            self.click_type()

        self.set_stations()
        self.click_station(self.plan['stations'][0])
        self.set_cycle_snd()
        self.set_hours_snd()
        self.click_back()

    def set_for_each(self):
        return

    def calc_total(self):
        total = len(self.plan['stations']) * len(self.plan['hours']) * self.get_site_count()
        return total

    def iterate_hours(self, what_for, station):
        for hour in self.plan['hours']:
            self.print_info_string(what_for, station, hour)
            self.click_hour(hour)
            self.make_screenshot(area='', hour=hour, what_for=what_for, product=station)
            self.click_back()

    def iterate_stations(self, what_for):
        for station in self.plan['stations']:
            self.click_station(station)
            self.click_cycle_snd()
            self.iterate_hours(what_for=what_for, station=station)
            self.click_back()

    def iterate_what_for(self):
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            self.click_type()
            self.click_tab()
            self.iterate_stations(what_for)
