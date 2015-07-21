from guitester import GuiTester
from pages.basepage import BasePage
from pages.dashboard import Dashboard

class GuiIAM(GuiTester):

    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        super(GuiIAM, self).__init__(console_url, webdriver_url=webdriver_url, sauce=sauce, browser=browser, version=version, platform=platform)
