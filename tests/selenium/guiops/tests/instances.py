from guitester.guiec2 import GuiEC2
import string, random, time


class Instance_operations_sequence(GuiEC2):

    def __init__(self):
        self.tester = GuiEC2("https://10.111.5.145","http://10.111.80.147:4444/wd/hub")

    def id_generator(self, size = 6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for j in range(size))

    def instance_ops_test(self):
        self.tester.login("ui-test-acct-00", "admin", "mypassword0")
        s_group1_name = self.id_generator()+"-group"
        s_group1=self.tester.create_security_group_from_view_page(s_group1_name, "Security group created by GUI test")
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
        self.tester.terminate_instance_from_view_page(instance2_name, instance2_id)
        self.tester.launch_more_like_this_from_detail_page(instance2_id, monitoring=True, user_data="Test user data.")
        self.tester.terminate_instance_from_detail_page(instance1_id)
        instance3_name = self.id_generator()+"-instance"
        self.tester.launch_instance_from_dashboard(image="centos", instance_name=instance3_name, availability_zone="one",
                                                            instance_type= "m1.small",security_group=s_group1_name, key_name=keypair1_name)
        self.tester.batch_terminate_all_instances()
        self.tester.delete_keypair_from_detail_page(keypair1_name)
        self.tester.delete_security_group_from_view_page(s_group1_name, s_group1_id)
        self.tester.logout()
        self.tester.exit_browser()

if __name__ == '__main__':
        tester = Instance_operations_sequence()
        Instance_operations_sequence.instance_ops_test(tester)