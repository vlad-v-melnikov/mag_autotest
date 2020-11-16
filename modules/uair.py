from modules.gfs_like import GfsLike
from retry import retry
import logging
import time

from selenium.common.exceptions import TimeoutException


class Uair(GfsLike):

    @retry(TimeoutException, tries=5, delay=2)
    def reset_to_base(self, what_for):
        site = self.settings.sites[what_for]
        url = f"{site}/observation-type-area.php#"

        if url != self.driver.current_url:
            self.driver.get(url)
        self.click_model()

    def click_model(self):
        try:
            self.hover_and_click('obstype_' + self.plan['model'])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking {self.plan['model']}")

    def click_area(self, area):
        try:
            self.hover_and_click('obsarea_' + area)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown while clicking {area}")

    def click_product(self, product):
        try:
            self.hover_and_click(product, type='link_text')
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {product} while clicking product")

    def click_cycle(self, **kwargs):
        area = next(iter(self.plan['area'].keys()))  # first area
        cycle = self.plan['area_cycle'][area]
        try:
            self.hover_and_click(cycle)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {cycle} while clicking cycle")

    def process_area(self, element):
        return element.text

    def get_all_area_ids(self):
        elements = self.driver.find_elements_by_xpath(
            "//a[contains(@id, 'obsarea') and not(contains(@class, 'deselect'))]")
        return elements

    def get_all_product_ids(self):
        elements = [elem.text for elem in
                    self.driver.find_elements_by_xpath(
                        "//a[contains(@class, 'bluehover') and not(contains(@class, 'cycle_link'))]")]
        return elements

    def set_common_for_all_areas(self):
        self.set_area_ids()
        area = next(iter(self.plan['area'].keys()))
        self.set_product_ids(area)
        self.set_cycle_id(area)

    def set_for_each_area(self):
        pass

    def calc_total(self):
        total_products = 0
        for area in self.plan['area']:
            total_products += len(self.plan['area'][area])
        total = total_products * self.get_site_count()
        return total

    def iterate_products(self, what_for, area):
        for product in self.plan['area'][area]:
            self.iterate_one_product(what_for, area, product)

    def iterate_one_product(self, what_for, area, product) -> None:
        first_area = next(iter(self.plan['area'].keys()))
        self.print_info_string(what_for, area, self.plan['area_cycle'][first_area], product)
        self.click_cycle(area=area, product=product)
        self.click_product(product)
        self.make_screenshot(area=area, what_for=what_for, product=product)
        self.click_back()

    def make_screenshot(self, **kwargs):
        area, what_for, product = kwargs.values()
        self.wait_image_page_load()
        time.sleep(self.settings.delays['image'])  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                     what_for + '_' +
                                     self.plan['model'] + '_' +
                                     area + '_' +
                                     product + '.png')
