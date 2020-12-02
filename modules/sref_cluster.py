import time
import random
import logging
from retry import retry
import modules.dimensions as dim

# selenium
from selenium.common.exceptions import TimeoutException

from modules.gfs_like import GfsLike


class SREFCluster(GfsLike):

    def set_hour_ids(self, area, product) -> None:
        super().set_hour_ids(area, product)
        for hour in self.plan[(area, product)]:
            self.click_hour(hour)
            time.sleep(self.settings.delays['common'])
            self.set_cluster_ids(area, product, hour)

    def set_cluster_ids(self, area, product, hour):
        elements = self.driver.find_elements_by_xpath("//a[contains(@onclick, 'open_cluster_page')]")
        if 'cluster_count' in self.plan.keys() \
                and 0 < self.plan['cluster_count'] <= len(elements):
            elements = random.sample(elements, self.plan['cluster_count'])
        self.plan[(area, product, hour)] = [element.text for element in elements]

    @retry(TimeoutException, tries=3, delay=1)
    def click_cluster(self, cluster):
        try:
            self.hover_and_click(cluster, 'link_text', force=True)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {cluster} while clicking this cluster")

    def screenshot_one_hour(self, **kwargs) -> None:
        area, hour, what_for, product, cluster = kwargs.values()
        try:
            self.click_hour(hour)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking hour")

        all_tabs_before = self.driver.window_handles
        time.sleep(self.settings.delays['common'])
        try:
            self.click_cluster(cluster)
        except Exception as e:
            logging.error(f"Exception {type(e)} was thrown for {hour}, {what_for}, {product} while clicking cluster")
            raise e

        # switching to new tab and closing it after screenshot
        new_tab = list(set(self.driver.window_handles) - set(all_tabs_before))[0]
        self.driver.switch_to.window(new_tab)
        self.make_screenshot(area=area, hour=hour, what_for=what_for, product=product, cluster=cluster)
        self.driver.close()
        self.driver.switch_to.window(self.handles[what_for])

    def make_screenshot(self, **kwargs):
        area, hour, what_for, product, cluster = kwargs.values()

        new_dim = {'width': dim.WINDOW_WIDTH, 'height': dim.WINDOW_HEIGHT}
        new_pos = self.driver.get_window_position()
        old_dim, old_pos = self.change_dim_and_pos(new_dim, new_pos)

        time.sleep(self.settings.delays['image'])  # let the image load
        self.driver.save_screenshot('screenshots/' +
                                    what_for + '_' +
                                    self.plan['model'] + '_' +
                                    area + '_' +
                                    product + '_' +
                                    hour + '_' +
                                    cluster.replace(' ', '-') + '.png')

        self.change_dim_and_pos(old_dim, old_pos)

    def iterate_one_product(self, what_for, area, product) -> None:
        for hour in self.plan[(area, product)]:
            for cluster in self.plan[(area, product, hour)]:
                self.print_info_string(what_for, area, cluster, product, hour)
                self.click_product(product)
                self.click_cycle(area=area, product=product)
                self.screenshot_one_hour(area=area, hour=hour, what_for=what_for, product=product,
                                         cluster=cluster)

    def calc_total(self):
        total_products = 0
        for area in self.plan['area']:
            total_products += len(self.plan['area'][area])
        hours = self.plan['hour_count']
        clusters = self.plan['cluster_count']
        total = total_products * hours * clusters * self.get_site_count()
        return total


if __name__ == "__main__":
    print("Not an application")
    exit(0)
