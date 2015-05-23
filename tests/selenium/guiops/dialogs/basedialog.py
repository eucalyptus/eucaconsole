from selenium_api.selenium_api import SeleniumApi
import time

class BaseDialog(SeleniumApi):

    def __init__(self, tester):
        self.tester = tester