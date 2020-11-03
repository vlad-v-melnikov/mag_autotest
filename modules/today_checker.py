from modules.settings import Settings
from modules.gfs_like import GfsLike
from pprint import pprint
from datetime import date


class TodayChecker:
    excluded_areas = ['PANELS', 'HRW-NMMB', 'HIRES-FV3']
    cycles_test = {}
    cycles_prod = {}

    def __init__(self, driver, handles):
        self.settings = Settings()
        self.models = self.settings.plan
        self.driver = driver
        self.handles = handles

    def save_cycles(self, what_for, dude):
        print(f"Saving cycles for {dude.plan['model']}")
        elements = dude.get_all_cycles()
        if what_for == 'test':
            self.cycles_test[dude.plan['model']] = [element.get_attribute('id') for element in elements]
        else:
            self.cycles_prod[dude.plan['model']] = [element.get_attribute('id') for element in elements]

    def has_today(self):
        no_today = []
        date_today = date.today().strftime("%Y%m%d")
        for model, times in self.cycles_test.items():
            date_only = [one_time[:8] for one_time in times]
            if date_today not in date_only:
                no_today.append(model)

        print(f"No today's date {date.today().strftime('%Y/%m/%d')} in:")
        pprint(no_today)

    def find_area_id(self):
        element = self.driver.find_element_by_xpath(
            "//a[contains(@id, 'modarea') and not(contains(@class, 'deselect'))]")
        assert element, 'No area found'
        return element.get_attribute('class')

    def check_today_now(self):
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
            dude.click_model()
            area = self.find_area_id()
            dude.click_area(area)
            self.save_cycles(what_for, dude)
            dude.click_back()

        print()
        self.has_today()

# for now, it only finds if there is a cycle for today for each of the models
