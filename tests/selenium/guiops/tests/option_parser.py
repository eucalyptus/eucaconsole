import argparse

class Option_parser(object):

    def parse_options(self):
        parser = argparse.ArgumentParser(description='Process options.')
        parser.add_argument('-c', '--console_url', type=str, help='Console url <example: https://10.111.1.7>')
        parser.add_argument('-w', '--web_driver', type=str, help='Remote_web_driver_url <example: http://10.111.80.147:4444/wd/hub>')
        args = vars(parser.parse_args())
        return args