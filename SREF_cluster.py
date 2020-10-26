import time
import random
import logging
from retry import retry
from datetime import date

# selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from settings import Settings
from screenshot_maker import ScreenshotMaker


class SREFCluster(ScreenshotMaker):
    IMAGE_DELAY = 1

    def __init__(self, model, driver, handles):
        super().__init__(model, driver, handles)

    def set_hour_ids(self, area_name, product) -> None:
        super().set_hour_ids(area_name, product)
        for hour in self.plan[(area_name, product)]:
            self.driver.find_element_by_id(hour).click()
            time.sleep(1)
            self.set_cluster_ids(area_name, product, hour)

    def set_cluster_ids(self, area_name, product, hour):
        elements = self.driver.find_elements_by_xpath("//a[contains(@onclick, 'open_cluster_page')]")
        if 'cluster_count' in self.plan.keys() \
                and 0 < self.plan['cluster_count'] <= len(elements):
            elements = random.sample(elements, self.plan['cluster_count'])
        self.plan[(area_name, product, hour)] = [element.text for element in elements]

    @retry(TimeoutException, tries=3, delay=2)
    def click_cluster(self, cluster):
        action = ActionChains(self.driver)
        element = self.driver.find_element_by_link_text(cluster)
        action.move_to_element(element).perform()
        time.sleep(1)
        element.click()

    def screenshot_one_hour(self, **kwargs) -> None:
        area, hour, what_for, product, cluster = kwargs.values()
        try:
            self.click_hour(hour)
            time.sleep(1)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking hour")

        all_tabs_before = self.driver.window_handles
        try:
            self.click_cluster(cluster)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking cluster")
            raise e
        time.sleep(1)

        # switching to new tab and closing it after screenshot
        new_tab = list(set(self.driver.window_handles) - set(all_tabs_before))[0]
        self.driver.switch_to.window(new_tab)
        self.make_screenshot(area=area, hour=hour, what_for=what_for, product=product, cluster=cluster)
        self.driver.close()
        self.driver.switch_to.window(self.handles[what_for])

    def make_screenshot(self, **kwargs):
        area, hour, what_for, product, cluster = kwargs.values()
        time.sleep(self.IMAGE_DELAY)  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                    what_for + '_' +
                                    self.plan['model'] + '_' +
                                    area + '_' +
                                    product + '_' +
                                    hour + '_' +
                                    cluster.replace(' ', '-') + '.png')

    def iterate_one_product(self, what_for, area_name, product, hours_just_set) -> None:
        for hour in self.plan[(area_name, product)]:
            for cluster in self.plan[(area_name, product, hour)]:
                print(f"Processing {what_for} {area_name} {product} {hour} {cluster}... ", end='')
                if not hours_just_set:
                    self.click_product(product)
                    self.click_cycle()
                print(
                    f"Clicked {what_for} {area_name} {product} {hour} for cycle {self.plan['cycle']} {cluster}... ")
                self.screenshot_one_hour(area=area_name, hour=hour, what_for=what_for, product=product,
                                         cluster=cluster)
                print("Done.")


if __name__ == "__main__":
    print("Not an application")
    exit(0)
