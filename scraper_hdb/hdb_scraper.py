from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


import pandas as pd
import time


class HdbScrape:

    def __init__(self):
        self.browser = webdriver.Chrome('../driver/chromedriver')
        self.timeout = 30

    def login(self):
        self.browser.get('https://app.dnbhoovers.com/')
        try:
            time.sleep(5)
            element_present = EC.presence_of_element_located((By.ID, 'username'))
            WebDriverWait(self.browser, self.timeout).until(element_present)

            time.sleep(5)
            user_element = self.browser.find_element_by_id('username')
            user_element.send_keys('')
            self.browser.find_element_by_class_name('continue-btn').click()
            time.sleep(5)

            self.browser.implicitly_wait(10)
            element_present = EC.presence_of_element_located((By.ID, 'password'))
            WebDriverWait(self.browser, self.timeout).until(element_present)

            time.sleep(5)
            pass_element = self.browser.find_element_by_id('password')
            pass_element.send_keys('')

            time.sleep(5)
            self.browser.find_element_by_class_name('continue-btn').click()

            try:
                search_url_list = self.get_search_lists()
            except Exception as e:
                self.browser.switch_to_window(self.browser.window_handles[1])

            for search_url in search_url_list:
                newDF = pd.DataFrame()
                try:
                    self.browser.get(search_url)
                    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'search-form-actions'))
                    WebDriverWait(self.browser, self.timeout).until(element_present)

                    time.sleep(5)

                    self.browser.find_element_by_class_name('search-form-actions')\
                        .find_element_by_class_name('btn').click()

                    time.sleep(5)

                    element_present = EC.presence_of_element_located((By.ID, 'gridDropdownContainer'))
                    WebDriverWait(self.browser, self.timeout).until(element_present)

                    self.browser.find_element_by_id('gridDropdownContainer').click()
                    self.browser.find_element_by_id('gridViewDropdown').find_element_by_class_name('grid-view').click()

                    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'search-result-download'))
                    WebDriverWait(self.browser, self.timeout).until(element_present)

                    time.sleep(5)

                    total_pages = int(self.browser.find_element_by_class_name('page-last').text)

                    for page in range(1, total_pages-1):
                        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'next-pg'))
                        WebDriverWait(self.browser, self.timeout).until(element_present)

                        table = self.browser.find_element_by_id('gridViewTable')
                        rows = table.find_elements_by_tag_name('tr')

                        for row in rows:
                            columns = row.find_elements_by_tag_name('td')

                            for column in columns:
                                print(column.text)
                        break

                        self.browser.find_element_by_class_name('next-pg').click()
                        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'next-pg'))
                        WebDriverWait(self.browser, self.timeout).until(element_present)
                        time.sleep(20)

                    time.sleep(10)

                except Exception as e:
                    pass

                break

            time.sleep(5)
            self.browser.implicitly_wait(10)
            self.logout()
        except TimeoutException:
            print("Timed out waiting for page to load")

    def logout(self):
        self.browser.find_element_by_xpath(u'//*[@id="drop-user"]').click()
        self.browser.find_element_by_xpath(u'//*[@id="navbar"]/div[1]/div/div[3]/ul/li/ul/li[2]/a').click()
        self.browser.quit()

    def get_search_lists(self):
        self.browser.execute_script("window.open();")
        self.browser.switch_to_window(self.browser.window_handles[1])
        self.browser.get("https://app.dnbhoovers.com/searches")

        time.sleep(5)
        element_present = EC.presence_of_element_located((By.ID, 'asset-list'))
        WebDriverWait(self.browser, self.timeout).until(element_present)

        list_elements = self.browser.find_elements_by_class_name('asset')

        search_url_list = []

        for saved_search in list_elements:
            saved_search_url = saved_search.find_element_by_class_name('search-label') \
                .find_element_by_tag_name('a') \
                .get_attribute('href')

            search_url_list.append(saved_search_url)

        time.sleep(7)

        return search_url_list

    def process_individual(self):
        pass

    def process__companies(self):
        pass


if __name__ == '__main__':
    scraper = HdbScrape()
    scraper.login()
