from panels import Panels
import time

class StormTracks(Panels):
    def find_cycle(self, cycles: list):
        if len(cycles) == 1:
            return cycles[0].get_attribute('id')

        cycles = [cycle.get_attribute('id') for cycle in cycles]
        fall_back = cycles.pop(0)
        for cycle_id in cycles:
            self.hover_and_click(cycle_id)
            hours = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
            if len(hours) > 0:
                return cycle_id

        return fall_back
