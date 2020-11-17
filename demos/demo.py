from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
import time
from retry import retry

# selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.color import Color
from selenium.webdriver.support.ui import WebDriverWait


class Main:

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.site = "https://magtest.ncep.noaa.gov/data/skewt/20201117/00/skewt_namer.html"
        self.driver.set_page_load_timeout(5)
        try:
            self.open_site()
        except TimeoutException:
            self.driver.close()

    @retry(TimeoutException, tries=5, delay=1)
    def open_site(self):
        self.driver.get(self.site)
        self.driver.maximize_window()

    def action_function(self):
        type = 'link_text'
        identifier = 'CWBK'
        force = True
        if type == 'link_text':
            xpath_str = f"//a[contains(text(), \"{identifier}\")]"
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_str)))
        else:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, identifier)))

        # element = self.driver.find_element_by_link_text(identifier)
        color = Color.from_string(element.value_of_css_property('color')).hex
        if force or color == '#0000ff':  # blue, not selected
            action = ActionChains(self.driver)
            try:
                action.move_to_element(element).perform()
            except MoveTargetOutOfBoundsException as e:
                print("Link is away from the screen, cannot do hover but can click.")
            time.sleep(1)
            element.click()
            time.sleep(1)

    def close_all(self):
        self.driver.close()


if __name__ == '__main__':
    main = Main()
    main.action_function()
    main.close_all()

