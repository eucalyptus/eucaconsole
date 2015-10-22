from guiops.guiops import GuiOps
from option_parser import Option_parser
import string, random, time



class Instance_operations_sequence(GuiOps):

    def __init__(self):
        parser = Option_parser()
        self.console_url = parser.parse_options()['console_url']
        self.webdriver_url = parser.parse_options()['web_driver']
        self.account = parser.parse_options()['account']
        self.user = parser.parse_options()['user_name']
        self.password = parser.parse_options()['password']
        self.sauce = parser.parse_options()['sauce']
        self.browser = parser.parse_options()['browser']
        self.version = parser.parse_options()['version']
        self.platform = parser.parse_options()['platform']
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url, sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)


    def instance_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        s_group1_name = self.id_generator()+"-group"
        s_group1=self.tester.create_security_group_from_view_page(s_group1_name, "Security group created by instance test")
        s_group1_id = s_group1.get("s_group_id")
        keypair1_name = self.id_generator()+"-key-pair"
        self.tester.create_keypair_from_dashboard(keypair1_name)
        instance1_name = self.id_generator()+"-instance"
        instance1 = self.tester.launch_instance_from_image_view_page(image_id_or_type="centos", instance_name=instance1_name,
                                                               instance_type= "m1.medium", security_group=s_group1_name, key_name=keypair1_name)
        instance1_id = instance1.get("instance_id")
        instance2_name = self.id_generator()+"-instance"
        instance2 = self.tester.launch_more_like_this_from_view_page(inatance_id=instance1_id, instance_name=instance2_name)
        instance2_id = instance2.get("instance_id")
        self.tester.terminate_instance_from_view_page(instance2_id, instance2_name)
        self.tester.launch_more_like_this_from_detail_page(instance2_id, monitoring=True, user_data="Test user data.")
        self.tester.terminate_instance_from_detail_page(instance1_id)
        instance3_name = self.id_generator()+"-instance"
        instance3=self.tester.launch_instance_from_dashboard(image="centos", instance_name=instance3_name, availability_zone="one",
                                                            instance_type= "m1.small",security_group=s_group1_name, key_name=keypair1_name)
        instance3_id = instance3.get("instance_id")
        self.tester.terminate_instance_from_detail_page(instance3_id)
        self.tester.batch_terminate_all_instances()
        instance4 = self.tester.launch_instance_from_dashboard(image="centos", availability_zone="one",
                                                            instance_type= "m1.large")
        instance4_id = instance4.get("instance_id")
        self.tester.terminate_instance_from_view_page(instance_id=instance4_id)
        self.tester.delete_keypair_from_detail_page(keypair1_name)
        self.tester.delete_security_group_from_view_page(s_group1_name, s_group1_id)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Instance_operations_sequence()
        Instance_operations_sequence.instance_ops_test(tester)
