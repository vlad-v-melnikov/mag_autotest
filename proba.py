from selenium import webdriver
from settings import Settings
from pprint import pprint
import time
from retry import retry
from timeout_decorator import timeout, TimeoutError


def get_site_with_retry(driver, site):
    return driver.get(site)


def main():
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    site = "https://magtest.ncep.noaa.gov"
    driver = get_site_with_retry(driver, site)
    driver.get(site)
    driver.close()

    # setting up the page
    # settings = Settings()
    #
    # driver.find_element_by_link_text(settings.links['section']).click()
    # driver.find_element_by_link_text(settings.links['model']).click()
    # driver.find_element_by_link_text(settings.links['area']).click()
    # driver.find_element_by_id('2020101306UTC').click()
    #
    # results = [elem.get_attribute('id') for elem in driver.find_elements_by_xpath("//a[contains(@class, 'params_link')]")]
    #
    # for result in results:
    #     driver.find_element_by_id(result).click()
    #     driver.find_element_by_id('fhr_id_060').click()
    #     time.sleep(1)
    #     driver.find_element_by_class_name('nav_button').click()


if __name__ == '__main__':
    main()