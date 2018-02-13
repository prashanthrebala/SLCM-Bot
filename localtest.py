from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import re
import sections
import prashanth

driver = webdriver.Chrome()
driver.get("http://slcm.manipal.edu/loginForm.aspx")
driver.find_element_by_id("txtUserid").send_keys(prashanth.username)
driver.find_element_by_id("txtpassword").send_keys(prashanth.password)
driver.find_element_by_css_selector('#btnLogin').click()
logged_in = True
while str(driver.current_url) == 'http://slcm.manipal.edu/loginForm.aspx':
    if "System doesn't recognize user id or password" in driver.page_source:
        # incorrect login details
        print 'invalid details'
        driver.refresh()
        logged_in = False
        break
    time.sleep(0.5)

if logged_in:
    print "Successfully logged in as " + \
          str(driver.find_element_by_id("lblUserName").get_attribute("innerHTML")).title()
else:
    print 'lmao rekt'
# print 'logged in'
# time.sleep(5)

"""
from telepot.loop import MessageLoop
import telepot


def handle(msg):
    telepot.glance(msg)
    print msg['text']


def flush():
    bot = telepot.Bot('441669105:AAH3Brfz_jw0np86aPv7AKgPzOA6kzkb4fs')
    MessageLoop(bot, handle).run_as_thread()
    
shounak: 432450177
"""