from guitester.guiec2 import GuiEC2
from guitester.guicf import GuiCF
from guitester.guiiam import GuiIAM
from guitester.guiasg import GuiASG
from guitester.guielb import GuiELB
from guitester.guis3 import GuiS3


class GuiOps(GuiEC2, GuiCF, GuiIAM, GuiASG, GuiS3):
    def __init__(self, console_url, sauce=False, webdriver_url=None, browser=None, version=None, platform=None):
        self.console_url = console_url
        self.sauce = sauce
        self.webdriver_url = webdriver_url
        self.browser = browser
        self.version = version
        self.platform =platform
