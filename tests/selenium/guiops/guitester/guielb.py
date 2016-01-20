from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard

class GuiELB(GuiTester):

    def __init__(self, console_url, chrome =True, firefox=False, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiELB, self).__init__(console_url, webdriver_url=webdriver_url, chrome= chrome, firefox=firefox, sauce=sauce, browser=browser, version=version, platform=platform)
