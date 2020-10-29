import time
import logging
from datetime import date
from retry import retry

from gfs_like import GfsLike


class Panels(GfsLike):

    def __init__(self, model, driver, handles):
        super().__init__(model, driver, handles)

    def iterate_products(self, what_for, area):
        hours_just_set = False
        for product in self.plan['area'][area]:
            if (area, product) not in self.plan.keys():
                self.click_product(product)
                self.set_cycle_id_panels(area, product)
                self.set_hour_ids(area, product)
                hours_just_set = True
            self.iterate_one_product(what_for, area, product, hours_just_set)

    def set_cycle_id_panels(self, area, product):
        time.sleep(2)
        cycles = self.get_cycles(area, product)
        self.plan[('cycle', area, product)] = cycles[1].get_attribute('id') if len(cycles) > 1 \
            else cycles[0].get_attribute('id')

    def click_cycle(self, **kwargs):
        area, product = kwargs.values()
        time.sleep(2)
        try:
            self.hover_and_click(self.plan[('cycle', area, product)])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {self.plan[('cycle', area, product)]} "
                          f"while clicking cycle")

    def iterate_one_product(self, what_for, area, product, hours_just_set) -> None:
        for hour in self.plan[(area, product)]:
            print(f"Processing {what_for} {area} {product} {hour}... ", end='')
            if not hours_just_set:
                self.click_product(product)
                self.click_cycle(area=area, product=product)
            print(f"Clicked {what_for} {area} {product} {hour} for cycle "
                  f"{self.plan[('cycle', area, product)]}... ")
            self.screenshot_one_hour(name=area, hour=hour, what_for=what_for, product=product)
            print("Done.")

    def set_common_for_all_areas(self):
        self.set_area_ids()

if __name__ == "__main__":
    print("Not an application")
    exit(0)

# To Do:
# 1) Test for all areas, one product, one hour. Attention to cycles.
