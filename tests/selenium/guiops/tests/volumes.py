from guitester.guiec2 import GuiEC2
import string, random, time


class Volume_operations_sequence(GuiEC2):

    def __init__(self):
        self.tester = GuiEC2("http://10.111.80.147:4444/wd/hub", "https://10.111.5.1")

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def volume_ops_test(self):
        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        volume1_name = self.id_generator()+"-volume"
        volume1 = self.tester.create_volume_from_view_page(volume1_name, volume_size=2, availability_zone="two")
        volume1_id = volume1.get("volume_id")
        self.tester.delete_volume_from_view_page(volume1_id)
        time.sleep(15)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Volume_operations_sequence()
        Volume_operations_sequence.volume_ops_test(tester)