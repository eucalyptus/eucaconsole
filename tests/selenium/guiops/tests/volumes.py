from guitester.guiec2 import GuiEC2
from option_parser import Option_parser
import string, random, time


class Volume_operations_sequence(GuiEC2):

    def __init__(self):
        parser = Option_parser()
        self.console_url = parser.parse_options()['console_url']
        self.webdriver_url = parser.parse_options()['web_driver']
        self.account = parser.parse_options()['account']
        self.user = parser.parse_options()['user_name']
        self.password = parser.parse_options()['password']
        self.tester = GuiEC2(console_url=self.console_url, webdriver_url=self.webdriver_url)

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def volume_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=2, availability_zone="one")
        volume1_id = volume1.get("volume_id")
        self.tester.delete_volume_from_view_page(volume1_id)
        time.sleep(15)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Volume_operations_sequence()
        Volume_operations_sequence.volume_ops_test(tester)