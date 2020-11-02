from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.color import Color

import time
from retry import retry

class Main:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.site = "https://mag.ncep.noaa.gov/model-guidance-model-area.php"
        self.driver.set_page_load_timeout(5)
        try:
            self.open_site()
        except TimeoutException as e:
            self.driver.close()

    @retry(TimeoutException, tries=5, delay=1)
    def open_site(self):
        self.driver.get(self.site)

    def close_all(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.close()

    def hover_and_click_id(self, id):
        element = self.driver.find_element_by_id(id)
        color = Color.from_string(element.value_of_css_property('color')).hex
        if color == '#0000ff': # blue
            print('Hover and click', id)
            action = ActionChains(self.driver)
            action.move_to_element(element).perform()
            time.sleep(1)
            element.click()
            time.sleep(1)

    def experiment(self):
        self.hover_and_click_id('modtype_PANELS')
        time.sleep(2)
        self.hover_and_click_id('modtype_PANELS')


if __name__ == '__main__':
    main = Main()

    main.experiment()

    main.close_all()