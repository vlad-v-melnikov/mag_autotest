from modules.uair import Uair
from retry import retry
from datetime import date
import logging
import random


class Skewt (Uair):

    def set_common_for_all(self):
        self.set_area_ids()
        area = next(iter(self.plan['area'].keys()))
        self.set_cycle_id(area)

    def save_cycle_to_plan(self, area, cycles):
        self.plan['area_cycle'][area] = cycles[1].text if len(cycles) > 1 \
            else cycles[0].text

    @retry(AssertionError, tries=3, delay=2)
    def get_all_cycles(self, area='', product=''):
        if self.settings.sites['today_only']:
            date_today = date.today().strftime("%Y%m%d")
            cycles = self.driver.find_elements_by_xpath(f"//a[contains(@href, 'skewt') "
                                                        f"and (contains(@title, '{date_today}'))]")
        else:
            cycles = self.driver.find_elements_by_xpath(f"//a[contains(@href, 'skewt')]")
        assert len(cycles) > 0, f'No cycles found {area}, {product}'
        return cycles

    def click_cycle(self, **kwargs):
        area = next(iter(self.plan['area'].keys()))  # first area
        cycle = self.plan['area_cycle'][area]
        try:
            self.hover_and_click(cycle, type='link_text')
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {cycle} while clicking cycle")

    def click_station(self, station):
        try:
            self.hover_and_click(station, type='link_text', force=True)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {station} while clicking product")

    def iterate_stations(self, what_for, area):
        # if stations are not set yet, set them
        if len(self.plan['area'][area]) == 0:
            self.set_stations(area)
        for station in self.plan['area'][area]:
            self.iterate_one_station(what_for, area, station)

    def set_stations(self, area):
        print(f"Setting stations for {area}...", end=' ')
        logging.info(f"Setting stations for {area}...")

        elements = self.get_all_station_texts()
        assert len(elements) > 0, "Empty stations"

        if 'station_count' in self.plan.keys() \
                and 0 < self.plan['station_count'] <= len(elements):
            elements = random.sample(elements, self.plan['station_count'])
        self.plan['area'][area] = elements
        print(f"{len(elements)} station(s) set.")
        logging.info(f"{len(elements)} station(s) set.")

    def get_all_station_texts(self):
        elements = [elem.text for elem in
                    self.driver.find_elements_by_xpath(
                        "//a[contains(@href, \"skewt\") and not(contains(@style,\"text-decoration\"))]")]
        return elements

    def iterate_one_station(self, what_for, area, station) -> None:
        first_area = next(iter(self.plan['area'].keys()))
        self.print_info_string(what_for, area, self.plan['area_cycle'][first_area], station)
        self.click_station(station)
        self.make_screenshot(area=area, what_for=what_for, product=station)
        self.click_back()

    def iterate_what_for(self):
        for what_for in self.settings.sites['order_of_iteration']:
            self.switch_to_window(what_for)
            for area in self.plan['area'].keys():
                self.reset_to_base(what_for)
                self.click_area(area)
                self.click_cycle(area=area)
                self.iterate_stations(what_for, area)
