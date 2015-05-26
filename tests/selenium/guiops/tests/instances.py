from guitester.guiec2 import GuiEC2
import string, random, time


class Instance_operations_sequence(GuiEC2):

    def __init__(self):
        self.tester = GuiEC2("http://10.111.80.147:4444/wd/hub", "http://10.111.5.145:8888")

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def instance_ops_test(self):

        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        #self.tester.launch_instance_from_dashboard()
        #self.tester.get_attrubute_by_css("#tableview>table>tbody>tr>td>a", "href")
        self.tester.get_attrubute_by_css("#item-dropdown_instances-running", "class")
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Instance_operations_sequence()
        Instance_operations_sequence.instance_ops_test(tester)