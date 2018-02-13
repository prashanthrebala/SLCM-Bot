from selenium import webdriver
from threading import Timer
import time
import sections


class User:

    def __init__(self):
        self.driver = None
        self.username = None
        self.password = None
        self.last_time_stamp = None
        self.logged_in = False
        self.current_tab = "new user"

    def begin_session(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://slcm.manipal.edu/loginForm.aspx")
        self.driver.find_element_by_id("txtUserid").send_keys(self.username)
        self.driver.find_element_by_id("txtpassword").send_keys(self.password)
        self.driver.find_element_by_css_selector('#btnLogin').click()
        successfully_logged_in = True
        while str(self.driver.current_url) == 'http://slcm.manipal.edu/loginForm.aspx':
            if "System doesn't recognize user id or password" in self.driver.page_source:
                # incorrect login details
                print 'invalid details'
                self.driver.refresh()
                successfully_logged_in = False
                break
            time.sleep(0.5)

        self.last_time_stamp = time.time()
        Timer(45.0, self.close_driver).start()
        if successfully_logged_in:
            self.logged_in = True
            self.current_tab = "home"
            return "Successfully logged in as " + \
                  str(self.driver.find_element_by_id("lblUserName").get_attribute("innerHTML")).title()
        else:
            self.current_tab = "asked for username"
            self.username = None
            self.password = None
            return 'Incorrect username or password.\n\nPlease enter your username'

    def perform_action(self, command):
        self.last_time_stamp = time.time()
        reply, self.current_tab = sections.perform_action(self.driver, self.current_tab, command)
        return reply

    def close_driver(self):
        print time.time() - self.last_time_stamp
        if time.time() - self.last_time_stamp >= 45:
            self.logged_in = False
            self.driver.close()
        else:
            Timer(30.0, self.close_driver).start()
