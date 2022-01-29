import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import bs4

TIMEOUT = 30 # wait for page to load at max TIMEOUT seconds

class Helper():
    def __init__(self, driver):
        self.driver = driver

    def __wait_until_timeout(self, id=None, name=None, class_name=None):
        try:
            element_present = None
            if id:
                element_present = EC.presence_of_element_located((By.ID, id))
            if name:
                element_present = EC.presence_of_element_located((By.NAME, name))
            if class_name:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, class_name))
            WebDriverWait(self.driver, TIMEOUT).until(element_present)
            print("Page loaded")
        except TimeoutException:
            print("Timed out waiting for page to load")

    def wait_until_timeout_by_id(self, id):
        self.__wait_until_timeout(id=id)

    def wait_until_timeout_by_name(self, name):
        self.__wait_until_timeout(name=name)        

    def wait_until_timeout_by_class_name(self, class_name):
        self.__wait_until_timeout(class_name=class_name)

@dataclass
class MemberInfo():
    member_name: str = None
    nric: str = None
    course_type: str = None
    vehicle_model: str = None
    account_balance: float = None
    membership_expiry_date: str = None


class Bbdc():
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.driver.maximize_window() # make the window full screen

        self.helper = Helper(self.driver)
        self.member_info = MemberInfo()

    def __add_member_info(self):
        self.helper.wait_until_timeout_by_name('topFrame') # blue info bar at top with image bbdc logo is an iframe
        topFrame = self.driver.find_element(by='name', value='topFrame')
        self.driver.switch_to.frame(topFrame)
        
        soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
        info_table = soup.select_one('table.toptxtbold')
        rows = info_table.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            # there are 5 tds in left and 5tds on the right side of table
            if len(tds) == 5:
                for i, td in enumerate(tds):
                    if td.string == 'Member Name:':
                        #print(tds[i+1].string)
                        self.member_info.member_name = tds[i+1].string
                        continue

                    if td.string == 'NRIC:':
                        self.member_info.nric = tds[i+1].string
                        continue

                    if td.string == 'Course Type:':
                        self.member_info.course_type = tds[i+1].string
                        continue

                    if td.string == 'Vehicle Model:':
                        self.member_info.vehicle_model = tds[i+1].string
                        continue                

                    if td.string == 'Account Balance:':
                        self.member_info.account_balance = tds[i+1].string
                        continue

                    if td.string == 'Membership Expiry Date:':
                        self.member_info.membership_expiry_date = tds[i+1].string
                        continue  


    def login(self):
        self.driver.get('https://info.bbdc.sg/members-login/')
        
        element = self.driver.find_element(by='name', value='txtNRIC')
        element.send_keys(self.username)
        element = self.driver.find_element(by='name', value='txtpassword')
        element.send_keys(self.password)

        login_btn = self.driver.find_element(by='name', value='btnLogin')
        login_btn.click()
        
        self.helper.wait_until_timeout_by_id('proceed-button')
        
        proceed_btn = self.driver.find_element(by='id', value='proceed-button')
        proceed_btn.click()

        self.helper.wait_until_timeout_by_name('topFrame')

        self.__add_member_info()
    
    

if __name__ == '__main__':
    bbdc = Bbdc(username='781W22101984', password='204107')
    bbdc.login()
    print(bbdc.member_info)

    
