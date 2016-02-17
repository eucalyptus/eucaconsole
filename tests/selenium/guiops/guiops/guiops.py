import string
import random

from guitester.guiec2 import GuiEC2
from guitester.guicf import GuiCF
from guitester.guiiam import GuiIAM
from guitester.guiasg import GuiASG
from guitester.guielb import GuiELB
from guitester.guis3 import GuiS3


class GuiOps(GuiEC2, GuiCF, GuiIAM, GuiASG, GuiS3, GuiELB):

    _default_chars = string.ascii_lowercase + string.digits

    def __init__(self, console_url, sauce=False, webdriver_url=None,
                 browser=None, version=None, platform=None):
        super(GuiOps, self).__init__(console_url, webdriver_url=webdriver_url,
                                     sauce=sauce, browser=browser,
                                     version=version, platform=platform)
        self.console_url = console_url
        self.sauce = sauce
        self.webdriver_url = webdriver_url
        self.browser = browser
        self.version = version
        self.platform = platform

    def id_generator(self, size=6, chars=_default_chars):
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def get_zones_from_options(options):
        """
        :param options: instance of argparse parser.parse_options
        :return: dict of zones keyed by index (e.g {0: 'one', 1: 'two'})
        :rtype: dict

        """
        return dict(enumerate(options['zones'].split(',')))
