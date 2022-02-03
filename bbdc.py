import time
from getpass import getpass
from datetime import datetime
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import bs4

from notifications import Gmail

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
        """The website page is built with iFrames. And very bad in terms of html, css coding standards. 
           Terrible code and even the sql query is stored in html page as the attributes.
           Anyway. Here are the iFrames and page layout:
            <frameset rows="89,*" frameborder="NO" border="0" framespacing="0"> 
            <frame name="topFrame" scrolling="NO" noresize="" src="inc-webpage/b-topnav.asp" cd_frame_id_="2fa8466da3caf01345d20749fa79bd94">
            <frameset rows="*,20" frameborder="NO" border="0" framespacing="0"> 
            <frameset cols="175,*" frameborder="NO" border="0" framespacing="0"> 
            <frame name="leftFrame" scrolling="AUTO" noresize="" src="inc-webpage/b-sidenav-3.asp">
            <frame name="mainFrame" src="b-default.asp">
            </frameset>
            <frame name="bottomFrame" scrolling="NO" noresize="" src="inc-webpage/b-footer.asp">  
            </frameset>
            </frameset>
        """
        self.helper.wait_until_timeout_by_name('topFrame') # blue info bar at top with image bbdc logo is an iframe
        top_frame = self.driver.find_element(By.NAME, 'topFrame')
        self.driver.switch_to.frame(top_frame)
        
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
                        dollar = tds[i+1].string
                        self.member_info.account_balance = float(dollar.replace('$', ''))
                        continue

                    if td.string == 'Membership Expiry Date:':
                        self.member_info.membership_expiry_date = datetime.strptime(tds[i+1].string, '%d %B %Y')
                        continue

        self.driver.switch_to.default_content()

    def __refresh_main_page(self):
        self.driver.get('http://www.bbdc.sg/bbdc/b-mainframe.asp')

    def login(self):
        self.driver.get('https://info.bbdc.sg/members-login/')
        
        element = self.driver.find_element(By.NAME, 'txtNRIC')
        element.send_keys(self.username)
        element = self.driver.find_element(By.NAME, 'txtpassword')
        element.send_keys(self.password)

        login_btn = self.driver.find_element(By.NAME, 'btnLogin')
        login_btn.click()
        
        self.helper.wait_until_timeout_by_id('proceed-button')
        
        proceed_btn = self.driver.find_element(By.ID, 'proceed-button')
        proceed_btn.click()

        self.helper.wait_until_timeout_by_name('topFrame')

        self.__add_member_info()

    def tp_simulater_booking(self):
        """Traffic Police Driving Simulater booking. This is one of the most difficult sessions to get.
        """
        print(self.driver.page_source)
        self.helper.wait_until_timeout_by_name('leftFrame')
        left_frame = self.driver.find_element(By.NAME, 'leftFrame')
        self.driver.switch_to.frame(left_frame)

#        print(self.driver.page_source)
        booking_link = self.driver.find_element(By.XPATH, '//a[@href="../b-selectTPDSModule.asp"]')
        booking_link.click()

        # now you have clicked the link in left nav. Switch to main page
        self.driver.switch_to.default_content()
        main_frame = self.driver.find_element(By.NAME, 'mainFrame')
        self.driver.switch_to.frame(main_frame)

        self.helper.wait_until_timeout_by_name('optTest')
        tp_module1 = self.driver.find_element(By.NAME, 'optTest')
        tp_module1.click()

        print('Selecting "TP Driving Simulator Module 1" and submitting')
        self.driver.find_element(By.NAME, 'btnSubmit').click()
        
        # the page loads in main_frame and we are still at it. Lets continue
        # print(self.driver.page_source)

        # keep on checking until some sessions are available for booking
        # select month, all session and all days and serach
        
        NUM_OF_MONTH_TO_SEARCH = 6
        for i in range(NUM_OF_MONTH_TO_SEARCH):
            self.__all_month_all_session_all_day(i)
            buttons = self.driver.find_elements(By.XPATH, '//input[@type="button"]')
            
            # if button count is only one then no slots avaliable (only back button)
            if len(buttons) > 1:
                self.driver.get_screenshot_as_file('tp_booking_slot_available.png')
                gmail = Gmail()
                gmail.send(
                    ['sachindangol@gmail.com', 'arthi.sniop@gmail.com'],
                    subject='BBDC TP Simulater Slot availability notification',
                    body="""
                        Hi,
                            Please find the attachment to see the currently available slots for BBDC TP Simulater.

                        Thanks.
                    """,
                    attachments=['./tp_booking_slot_available.png']
                )
                print("Gmail notification sent.")
                break
            else:
                back_button = self.driver.find_element(By.NAME, 'btnBack')
                back_button.click()
                self.helper.wait_until_timeout_by_name('btnSearch')

    def __all_month_all_session_all_day(self, month_index):
        # select first month, all session and all days and serach first
        months = self.driver.find_elements(By.NAME, 'Month')

        if not months[month_index].is_selected():
            months[month_index].click()
        
        # uncheck already searched months which doesn't have slot for booking and select only current month_index month
        for i in reversed(range(month_index)):
            if months[i].is_selected():
                months[i].click()

        # just delay 1 sec so that user can see what has been done. Not required otherwise.
        time.sleep(1)

        session = self.driver.find_element(By.NAME, 'allSes')
        if not session.is_selected():
            session.click()

        time.sleep(1)        

        all_days = self.driver.find_element(By.NAME, 'allDay')
        if not all_days.is_selected():
            all_days.click()

        time.sleep(1)

        search = self.driver.find_element(By.NAME, 'btnSearch')
        search.click()

        time.sleep(1)
        self.helper.wait_until_timeout_by_name('btnBack') # just make sure that the page is loaded. At least back button is there.


if __name__ == '__main__':
    username = '279G23061987'
    print(f'username is {username}')
    print(f'key in password: ')
    password = getpass()
    bbdc = Bbdc(username=username, password=password)
#    bbdc = Bbdc(username='781W22101984', password='204107')
    bbdc.login()
    print(bbdc.member_info)
    bbdc.tp_simulater_booking()

    
