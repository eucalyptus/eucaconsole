import argparse

class Option_parser(object):

    def parse_options(self):
        parser = argparse.ArgumentParser(description='Process options.')
        parser.add_argument('-c', '--console_url', type=str, help='Console url <example: https://10.111.1.7>')
        parser.add_argument('-w', '--web_driver', type=str, help='Remote_web_driver_url <example: http://10.111.80.147:4444/wd/hub>')
        parser.add_argument('-u', '--user_name', type=str, help='User name')
        parser.add_argument('-a', '--account', type=str, help='Account')
        parser.add_argument('-p', '--password', type=str, help='Password')
        args = vars(parser.parse_args())
        return args