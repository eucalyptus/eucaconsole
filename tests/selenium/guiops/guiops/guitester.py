from selenium import webdriver
import unittest

class Config(object):

    webdriver_url = "http://10.111.80.126:4444/wd/hub"
    console_url = "https://10.111.5.175"
    account = "ui-test-acct-00"
    user = "admin"
    password = "mypassword0"

    implicit_wait=60



class GuiTester(object):
        def setUp(self):
            self.driver = webdriver.Remote(Config.webdriver_url, webdriver.DesiredCapabilities.FIREFOX)
            self.driver.implicitly_wait(Config.implicit_wait)
            self.driver.maximize_window()
            self.driver.get(Config.console_url)


        def TearDown(self):
            self.driver.quit()






