import argparse

class Option_parser(object):

    def parse_options(self):
        parser = argparse.ArgumentParser(description='Process options.')
        parser.add_argument('-c', '--console_url', type=str, help='Console url <example: https://10.111.1.7>')
        parser.add_argument('-w', '--web_driver', type=str, help='Remote_web_driver_url <example: http://10.111.80.147:4444/wd/hub>')
        parser.add_argument('-u', '--user_name', type=str, help='User name')
        parser.add_argument('-a', '--account', type=str, help='Account')
        parser.add_argument('-p', '--password', type=str, help='Password')
        parser.add_argument('--browser', type=str, help='Browser type for SuceLabs Testing, can be "ie", "chrome" or "firefox"')
        parser.add_argument('--version', type=str, help='Browser version for SuceLabs Testing, can be a number')
        parser.add_argument('--platform', type=str, help='Platform for SuceLabs Testing, can be "Windows XP", "Windows 7", "Windows 8", "Windows 8.1", "Linux" etc.')
        parser.add_argument('-s', '--sauce', dest='sauce', action='store_true', help='Use SauceLabs webdriver')
        parser.set_defaults(sauce=False)
        parser.add_argument('-z', '--zones', dest='zones', type=str,
                            help='Availability zones, pass as a comma-delimited list (e.g. "one,two")')
        parser.set_defaults(zones='one,two')
        args = vars(parser.parse_args())
        return args
