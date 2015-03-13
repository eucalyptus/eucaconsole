import unittest

from selenium import webdriver
from guiops.utilities import  Utilities


class BaseTestCase(Utilities):

    webdriver_url = "http://10.111.80.126:4444/wd/hub"
    console_url = "https://10.111.5.175"
    account = "ui-test-acct-00"
    user = "admin"
    password = "mypassword0"
    implicit_wait=60

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Remote(cls.webdriver_url, webdriver.DesiredCapabilities.FIREFOX)
        cls.driver.implicitly_wait(cls.implicit_wait)
        cls.driver.maximize_window()
        cls.driver.get(cls.console_url)
    


    @classmethod
    def tearDownClass (cls):
        cls.driver.quit()


        #self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
