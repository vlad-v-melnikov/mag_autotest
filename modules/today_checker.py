from modules.settings import Settings
from modules.gfs_like import GfsLike
from modules.uair import Uair
from modules.skewt import Skewt
from modules.trop import Trop
from modules.soundings import Soundings
from pprint import pprint
from datetime import date, datetime

CLASS_MAP = {
        'UAIR': Uair,
        'RTMA': Uair,
        'SKEWT': Skewt,
        'TROP': Trop,
        'GFS-SND': Soundings,
        'NAM-SND': Soundings,
    }

class TodayChecker:
    excluded_models = ['PANELS', 'HRW-NMMB', 'HIRES-FV3', 'GFS-SND']
    cycles = {}

    def __init__(self, driver, handles, filename="yaml/settings_check_today.yaml"):
        self.settings_file = filename
        self.settings = Settings(filename)
        self.models = self.settings.plan
        self.driver = driver
        self.handles = handles

    def save_cycles(self, what_for, dude, counter, total):
        print(f"Model {counter} out of {total}: saving cycles for {dude.plan['model']}")
        elements = dude.get_all_cycles()
        self.cycles[dude.plan['model']] = [element.get_attribute('title') for element in elements]

    def find_no_today(self):
        no_today = []
        date_today = date.today().strftime("%Y%m%d")
        for model, times in self.cycles.items():
            date_only = [one_time[:8] for one_time in times]
            if date_today not in date_only:
                no_today.append(model)

        return no_today

    def print_results(self, no_today):
        print(f"No today's date {datetime.now().strftime('%Y/%m/%d %H:%M:%S')} in:")
        pprint(no_today)

    def save_results(self, no_today):
        now = datetime.now()
        report_time = now.strftime("%Y%m%d%H%M%S")
        with open(f'reports/today_check_report_{report_time}.txt', 'w') as report_file:
            print(f"No today's date {datetime.now().strftime('%Y/%m/%d %H:%M:%S')} in:", file=report_file)
            pprint(no_today, stream=report_file)

    def find_area_id(self, prefix='modarea'):
        element = self.driver.find_element_by_xpath(
            f"//a[contains(@id, \"{prefix}\") and not(contains(@class, 'deselect'))]")
        assert element, 'No area found'
        return element.text

    def iterate_model_guidance(self, what_for, counter, total, models):
        first = True
        for model in models:
            if model in self.excluded_models:
                continue
            counter += 1
            dude = GfsLike(model, self.driver, self.handles, filename=self.settings_file)
            if first:
                dude.setup_page(what_for)
                first = False
            dude.plan['area_count'] = 0
            dude.click_model()
            area = self.find_area_id()
            dude.click_area(area)
            self.save_cycles(what_for, dude, counter, total)
            dude.click_back()
        return counter

    def iterate_observations(self, what_for, counter, total, models):
        first = True
        for model in models:
            if model in self.excluded_models:
                continue
            counter += 1
            dude = CLASS_MAP[model](model, self.driver, self.handles, filename=self.settings_file)
            if first:
                dude.setup_page(what_for)
                first = False
            dude.plan['area_count'] = 0
            dude.click_model()
            area = self.find_area_id(prefix='obsarea')
            dude.click_area(area)
            self.save_cycles(what_for, dude, counter, total)
            dude.click_back()
        return counter

    def iterate_trop(self, what_for, counter, total, models):
        first = True
        for model in models:
            if model in self.excluded_models:
                continue
            counter += 1
            dude = CLASS_MAP[model](model, self.driver, self.handles, filename=self.settings_file)
            if first:
                dude.setup_page(what_for)
                first = False
            dude.plan['area_count'] = 0

            elements = dude.get_all_storms()
            assert len(elements) > 0, 'No storms found'
            dude.click_storm(elements[-1].text)

            elements = dude.get_all_types()
            assert len(elements) > 0, 'No types found'
            dude.click_type(elements[0].text)

            self.save_cycles(what_for, dude, counter, total)
            dude.click_back()
        return counter

    def iterate_soundings(self, what_for, counter, total, models):
        first = True
        for model in models:
            if model in self.excluded_models:
                continue
            counter += 1
            dude = CLASS_MAP[model](model, self.driver, self.handles, filename=self.settings_file)
            if first:
                dude.setup_page(what_for)
                first = False
            dude.plan['station_count'] = 0

            dude.click_type()
            dude.click_tab()
            elements = dude.get_all_stations()
            assert len(elements) > 0, 'No stations found'
            dude.click_station(elements[0])
            self.save_cycles(what_for, dude, counter, total)
            dude.click_back()
        return counter

    def check_today_now(self):
        what_for = 'test'
        counter = 0

        model_guidance_models = [model for model in self.settings.plan.keys()
                                 if self.settings.plan[model]['section'] == 'Model Guidance']
        observation_models = [model for model in self.settings.plan.keys()
                                 if self.settings.plan[model]['section'] == 'Observations and Analyses']
        trop_models = [model for model in self.settings.plan.keys()
                              if self.settings.plan[model]['section'] == 'Tropical Guidance']
        sounding_models = [model for model in self.settings.plan.keys()
                              if self.settings.plan[model]['section'] == 'Forecast Soundings']
        total = len(set(model_guidance_models + observation_models + trop_models + sounding_models)
                    - set(self.excluded_models))

        counter = self.iterate_model_guidance(what_for, counter, total, model_guidance_models)
        counter = self.iterate_observations(what_for, counter, total, observation_models)
        counter = self.iterate_trop(what_for, counter, total, trop_models)
        self.iterate_soundings(what_for, counter, total, sounding_models)

        print()
        results = self.find_no_today()
        self.print_results(results)
        self.save_results(results)

