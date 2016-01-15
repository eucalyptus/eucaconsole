from guiops.guiops import GuiOps
from option_parser import Option_parser


class ElasticIPsOperationsSequence(GuiOps):

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
        self.tester = GuiOps(console_url=self.console_url, webdriver_url=self.webdriver_url,
                             sauce=self.sauce, browser=self.browser, version=self.version, platform=self.platform)

    def elastic_ip_ops_test(self):
        self.tester.login(self.account, self.user, self.password)
        self.elastic_ip_single_allocate_release_test_from_lp()
        self.elastic_ips_multi_allocate_release_test_from_dashboard()
        self.elastic_ips_associate_disassociate_ip()
        self.tester.logout()
        self.tester.exit_browser()

    def elastic_ip_single_allocate_release_test_from_lp(self):
        elastic_ips = self.tester.allocate_eip_from_lp(1)
        self.tester.release_eip_from_eip_lp(elastic_ips[0])

    def elastic_ips_multi_allocate_release_test_from_dashboard(self):
        elastic_ips = self.tester.allocate_eip_from_dashboard(2)
        released_ips = self.tester.release_eips_from_eip_lp(elastic_ips)
        assert elastic_ips == released_ips

    def elastic_ips_associate_disassociate_ip(self):
        elastic_ip = self.tester.allocate_eip_from_dashboard(1)
        elastic_ip = str(elastic_ip[0])
        launch_instance = self.tester.launch_instance_from_dashboard(instance_type="m1.medium")
        instance_id = launch_instance['instance_id']
        self.tester.associate_eip_from_eip_lp(elastic_ip, instance_id)
        self.tester.disassociate_eip_from_eip_lp(elastic_ip, instance_id)
        self.tester.associate_eip_from_eip_detail_page(elastic_ip, instance_id)
        self.tester.disassociate_eip_from_eip_detail_page(elastic_ip, instance_id)
        self.tester.associate_eip_from_instances_lp(elastic_ip, instance_id)
        self.tester.disassociate_eip_from_instances_lp(elastic_ip, instance_id)
        self.tester.associate_eip_from_instance_detail_page(elastic_ip, instance_id)
        self.tester.disassociate_eip_from_instance_detail_page(elastic_ip, instance_id)
        self.tester.terminate_instance_from_view_page(instance_id)
        self.tester.release_eip_from_eip_lp(elastic_ip)

if __name__ == '__main__':
        tester = ElasticIPsOperationsSequence()
        ElasticIPsOperationsSequence.elastic_ip_ops_test(tester)
