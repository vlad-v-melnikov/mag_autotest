from settings import Settings
from gfs_like import GfsLike
from pprint import pprint
import time


class CycleMatcher:
    excluded_areas = ['PANELS', 'HRW-NMMB', 'HIRES-FV3']
    cycles = {}

    def __init__(self, driver, handles):
        self.settings = Settings()
        self.models = self.settings.plan
        self.driver = driver
        self.handles = handles

    def save_cycles(self, what_for, dude):
        print(f"Saving cycles for {dude.plan['model']}")
        elements = dude.get_all_cycles()
        self.cycles[(what_for, dude.plan['model'])] = [element.get_attribute('id') for element in elements]

    def match_now(self):
        what_for = 'test'
        first = True

        for model in self.settings.plan.keys():
            if model in self.excluded_areas:
                continue

            dude = GfsLike(model, self.driver, self.handles)
            if first:
                dude.setup_page(what_for)
                first = False
            dude.plan['area_count'] = 0
            dude.set_area_ids()
            area = next(iter(dude.plan['area'].keys()))
            dude.click_area(area)
            self.save_cycles(what_for, dude)
            dude.click_back()

        print()
        pprint(self.cycles)
