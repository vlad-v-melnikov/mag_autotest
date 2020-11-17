import time
import logging

from modules.gfs_like import GfsLike


class Panels(GfsLike):

    def iterate_products(self, what_for, area):
        hours_just_set = False
        for product in self.plan['area'][area]:
            if (area, product) not in self.plan.keys():
                self.click_product(product)
                time.sleep(self.settings.delays['common'])
                self.set_cycle_id_per_product(area, product)
                self.set_hour_ids(area, product)
            self.iterate_one_product(what_for, area, product)

    def set_cycle_id_per_product(self, area, product):
        # no manual setting of cycles for panels
        self.click_product(product)
        time.sleep(self.settings.delays['common'])
        cycles = self.get_all_cycles(area, product)
        self.plan[('cycle', area, product)] = self.find_cycle(cycles)

    def find_cycle(self, cycles: list):
        return cycles[1].get_attribute('id') if len(cycles) > 1 else cycles[0].get_attribute('id')

    def click_cycle(self, **kwargs):
        area, product = kwargs.values()
        time.sleep(self.settings.delays['common'])
        try:
            self.hover_and_click(self.plan[('cycle', area, product)])
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {self.plan[('cycle', area, product)]} "
                          f"while clicking cycle")

    def iterate_one_product(self, what_for, area, product) -> None:
        for hour in self.plan[(area, product)]:
            self.print_info_string(what_for, area, self.plan[('cycle', area, product)], product, hour)
            self.click_product(product)
            time.sleep(self.settings.delays['common'])
            self.click_cycle(area=area, product=product)
            self.screenshot_one_hour(name=area, hour=hour, what_for=what_for, product=product)

    def set_common_for_all(self):
        self.set_area_ids()

    def set_for_each(self):
        counter = 0
        total = len(self.plan['area'].keys())
        for area in self.plan['area'].keys():
            counter += 1
            print(f"Area {counter} out of {total}:")
            logging.info(f"Area {counter} out of {total}:")
            self.set_product_ids(area)


if __name__ == "__main__":
    print("Not an application")
    exit(0)

# To Do:
# 1) Test for all areas, one product, one hour. Attention to cycles.
