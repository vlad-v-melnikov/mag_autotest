import unittest
import time
import random
import os
import glob
import pyautogui
from test_template import TestParent
from settings import Settings


def clear_screenshots():
    files = glob.glob('./screenshots/*.png')
    for f in files:
        os.unlink(f)


class MagTestTester(TestParent):

    def setUp(self) -> None:
        super().setUp()
        self.settings = Settings()

    def test_GFS_NAMER_single_product(self):
        types = ['test', 'prod']
        sites = [
            "https://magtest.ncep.noaa.gov",
            "https://mag.ncep.noaa.gov",
        ]
        links = {
            'section': 'MODEL GUIDANCE',
            'model': 'GFS',
            'area': 'NAMER',
            'cycle': '2020101306UTC',
            'product': 'precip_p06',
        }

        clear_screenshots()

        selected_element_ids = []
        for ty, site in zip(types, sites):
            self.driver.get(site)

            self.driver.find_element_by_link_text(links['section']).click()
            self.driver.find_element_by_link_text(links['model']).click()
            self.driver.find_element_by_link_text(links['area']).click()
            self.driver.find_element_by_id(links['cycle']).click()
            self.driver.find_element_by_id(links['product']).click()

            if not selected_element_ids:
                elements = self.driver.find_elements_by_xpath("//a[contains(@id, 'fhr_id_')]")
                sample = random.sample(range(len(elements)), self.settings.SAMPLE_NUMBER)
                selected_element_ids = [elements[i].get_attribute('id') for i in sample]

            for iden in selected_element_ids:
                self.driver.find_element_by_id(iden).click()
                time.sleep(1)  # let the image load
                screenshot_region = self.settings.SCREENSHOT_REGION
                region = screenshot_region
                pyautogui.screenshot('screenshots/' + ty + '_' + iden + '.png', region=region)
                self.driver.find_element_by_class_name('nav_button').click()


if __name__ == "__main__":
    unittest.main()
