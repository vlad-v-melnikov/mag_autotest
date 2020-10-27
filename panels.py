import time
import logging
from datetime import date

from screenshot_maker import ScreenshotMaker


class Panels(ScreenshotMaker):

    def __init__(self, model, driver, handles):
        super().__init__(model, driver, handles)

    def iterate_products(self, what_for, area_name):
        hours_just_set = False
        for product in self.plan['area'][area_name]:
            if (area_name, product) not in self.plan.keys():
                self.set_cycle_id_panels(area_name, product)
                self.set_hour_ids(area_name, product)
                hours_just_set = True
            self.iterate_one_product(what_for, area_name, product, hours_just_set)

    def set_cycle_id_panels(self, area_name, product):
        self.click_product(product)
        time.sleep(1)
        date_today = date.today().strftime("%Y%m%d")
        cycles = self.driver.find_elements_by_xpath(f"//a[contains(@class, 'cycle_link') "
                                                    f"and (contains(@id, {date_today}))]")
        self.plan[('cycle', area_name, product)] = cycles[1].get_attribute('id') if len(cycles) > 1 \
            else cycles[0].get_attribute('id')
        print(self.plan[('cycle', area_name, product)])

    def click_cycle(self, **kwargs):
        area, product = kwargs.values()
        try:
            self.hover_and_click_id(self.plan[('cycle', area, product)])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {self.plan[('cycle', area, product)]} "
                          f"while clicking cycle")

    def iterate_one_product(self, what_for, area_name, product, hours_just_set) -> None:
        print(self.plan[(area_name, product)])
        for hour in self.plan[(area_name, product)]:
            print(f"Processing {what_for} {area_name} {product} {hour}... ", end='')
            if not hours_just_set:
                self.click_product(product)
                self.click_cycle(area=area_name, product=product)
            print(f"Clicked {what_for} {area_name} {product} {hour} for cycle "
                  f"{self.plan[('cycle', area_name, product)]}... ")
            self.screenshot_one_hour(name=area_name, hour=hour, what_for=what_for, product=product)
            print("Done.")

    def set_common(self):
        self.set_area_ids()


if __name__ == "__main__":
    print("Not an application")
    exit(0)
