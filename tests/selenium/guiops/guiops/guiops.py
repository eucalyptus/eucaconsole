import logging
import string
import sys
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
        self.logger = self.create_logger()

    def id_generator(self, size=6, chars=_default_chars):
        return ''.join(random.choice(chars) for _ in range(size))

    def create_logger(self,
                 parent_logger_name = 'guitester',
                 identifier="guilogger",
                 stdout_level="debug",
                 stdout_format = None,
                 logfile = "",
                 logfile_level="debug",
                 make_log_file_global=True,
                 use_global_log_files=True,
                 file_format = None,
                 clear_file = False):
        default_format = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
        logger = logging.Logger(parent_logger_name)
        stdout_level = getattr(logging, stdout_level.upper(), logging.DEBUG)
        logfile_level = getattr(logging, logfile_level.upper(), logging.DEBUG)

        #Create stdout handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(default_format)
        logger.addHandler(stdout_handler)
        logger.setLevel(stdout_level)
        #Create a file handler...

        if logfile:
            file_hdlr = logging.FileHandler(logfile)
            file_hdlr.setFormatter(default_format)
            file_hdlr.setLevel(logfile_level)
            logger.addHandler(file_hdlr)
        return logger



