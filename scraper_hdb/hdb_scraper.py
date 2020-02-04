from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd
import time
import traceback
import re


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
            user_element.send_keys('xxxx')
            self.browser.find_element_by_class_name('continue-btn').click()
            time.sleep(5)

            self.browser.implicitly_wait(10)
            element_present = EC.presence_of_element_located((By.ID, 'password'))
            WebDriverWait(self.browser, self.timeout).until(element_present)

            time.sleep(5)
            pass_element = self.browser.find_element_by_id('password')
            pass_element.send_keys('xxxx')

            time.sleep(5)
            self.browser.find_element_by_class_name('continue-btn').click()

            search_url_list = []

            try:
                search_url_list = self.get_search_lists()
            except Exception as e:
                self.browser.switch_to_window(self.browser.window_handles[1])

            for search_url in search_url_list:
                if search_url == "https://app.dnbhoovers.com/search/saved/730a3d52-84af-4995-8439-2191ad3f6877":
                    self.process_individual(search_url)

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

        time.sleep(15)
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

    def process_individual(self, search_url):
        try:
            self.browser.get(search_url)
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'search-form-actions'))
            WebDriverWait(self.browser, self.timeout).until(element_present)

            time.sleep(5)

            self.browser.find_element_by_class_name('search-form-actions') \
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

            leads = []
            companies_list = set()
            companies_list.clear()
            file_name = ''

            for page in range(1, total_pages - 1):
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'next-pg'))
                WebDriverWait(self.browser, self.timeout).until(element_present)

                file_name = self.browser.find_element_by_class_name('save-search-title') \
                    .find_element_by_class_name('search-title').text
                file_name = re.sub("[^a-zA-Z0-9 \n\.]", '', file_name)
                table = self.browser.find_element_by_id('gridViewTable')
                rows = table.find_elements_by_tag_name('tr')

                for row in rows:
                    lead_dict = {}
                    columns = row.find_elements_by_tag_name('td')

                    lead_dict['First_Name'] = columns[0].text
                    lead_dict['Last_Name'] = columns[1].text
                    lead_dict['Title'] = columns[2].text
                    lead_dict['Company_Name'] = columns[3].text
                    lead_dict['Email'] = columns[4].text
                    lead_dict['Phone'] = columns[5].text
                    lead_dict['URL'] = columns[6].text
                    lead_dict['Employees'] = columns[7].text
                    lead_dict['Country_Region'] = columns[8].text
                    lead_dict['Address_Line_1'] = columns[9].text
                    lead_dict['Area_Code'] = columns[10].text
                    lead_dict['City'] = columns[11].text
                    lead_dict['State_Provience'] = columns[12].text
                    lead_dict['Direct_Marketing_Status'] = columns[13].text

                    companies_list.add(columns[3].find_element_by_tag_name('a').get_attribute('href'))

                    leads.append(lead_dict)

                self.browser.find_element_by_class_name('next-pg').click()
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'next-pg'))
                WebDriverWait(self.browser, self.timeout).until(element_present)

                time.sleep(20)
                break

            writer = pd.ExcelWriter(f'individuals/{file_name}_individual.xlsx', engine='xlsxwriter')
            df = pd.DataFrame(leads)
            df.to_excel(writer, engine='xlsxwriter', index=False, sheet_name='Sheet1')
            writer.save()
            print(f"Completed writing the file {file_name}")
            self.process_companies(companies_list, file_name)

        except Exception:
            traceback.print_exc()

    def process_companies(self, companies_list, file_name):

        company_list_details = []
        for company in companies_list:
            company_detail = {}
            self.browser.get(company)

            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'company-address'))
            WebDriverWait(self.browser, self.timeout).until(element_present)
            time.sleep(10)

            company_detail["Company_Name"] = self.browser.find_element_by_class_name("summary-container")\
                .find_element_by_class_name("title-row")\
                .find_element_by_class_name("name").text

            company_detail["Company_Address"] = self.browser.find_element_by_class_name("company-address-123").text

            data_containers = self.browser.find_elements_by_class_name('data-container')

            company_detail["Phone"] = ""
            company_detail["Employees"] = ""
            company_detail["Company Type"] = ""
            company_detail["Parent"] = ""
            company_detail["Corporate Family"] = ""
            company_detail["DUNS Number"] = ""
            company_detail["Key ID Number"] = ""
            company_detail["LEI Number"] = ""
            company_detail["Industry"] = ""
            company_detail["Reporting Currency"] = ""
            company_detail["Annual Sales:"] = ""
            company_detail["url"] = ""

            for container in data_containers:

                label = ""
                value = ""
                try:
                    label = container.find_element_by_class_name('data-label').text
                    value = container.find_element_by_class_name('data-value').text

                except Exception as e:
                    traceback.print_exc()
                    value = container.find_element_by_class_name('data-value').\
                        find_element_by_tag_name('a')\
                        .get_attribute('href')

                if label == "Tel:":
                    company_detail["Phone"] = value

                elif label == "Employees:":
                    company_detail["Employees"] = value

                elif label == "Company Type:":
                    company_detail["Company Type"] = value

                elif label == "Parent:":
                    company_detail["Parent"] = value

                elif label == "Corporate Family:":
                    company_detail["Corporate Family"] = value

                elif label == "D-U-N-S® Number:":
                    company_detail["DUNS Number"] = value

                elif label == "Key ID℠ Number:":
                    company_detail["Key ID Number"] = value

                elif label == "LEI Number:":
                    company_detail["LEI Number"] = value

                elif label == "Industry:":
                    company_detail["Industry"] = value

                elif label == "Reporting Currency:":
                    company_detail["Reporting Currency"] = value

                elif label == "Annual Sales::":
                    company_detail["Annual Sales:"] = value

                else:
                    company_detail["url"] = value

                print(f"{label}{value}")

            company_list_details.append(company_detail)

            writer = pd.ExcelWriter(f'company/{file_name}_company.xlsx', engine='xlsxwriter')
            df = pd.DataFrame(company_list_details)
            df.to_excel(writer, engine='xlsxwriter', index=False, sheet_name='Sheet1')
            writer.save()


if __name__ == '__main__':
    scraper = HdbScrape()
    scraper.login()
