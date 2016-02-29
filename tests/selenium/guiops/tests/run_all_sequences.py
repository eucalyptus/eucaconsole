from guiops.guiops import GuiOps
from option_parser import Option_parser
from keypair import Keypair_operations_sequence
from security_groups import Security_group_operations_sequence
from instances import Instance_operations_sequence
from volumes import VolumeOperationsSequence
from snapshots import SnapshotOperationsSequence
from autoscaling import AutoScalingOperationsSequence
from buckets import Buckets_operations_sequence
from elastic_ips import ElasticIPsOperationsSequence
import string, random, time
import logging, traceback

class Complete_sequence(GuiOps):

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
        #logging.basicConfig(format='%(asctime)s %(message)s')


    def run_all_tests(self):

        all_tests_capital = ["Keypair", "Security Group", "Instance", "Volume", "Snapshot", "Bucket", "Autoscaling", "Elastic IPs"]
        all_tests_lowercase = ["keypair", "security group", "instance", "volume", "snapshot", "bucket", "autoscaling", "elastic IPs"]
        sequences = [Keypair_operations_sequence().keypair_ops_test(), Security_group_operations_sequence().security_group_ops_test(),
                     Instance_operations_sequence().instance_ops_test(), VolumeOperationsSequence().volume_ops_test(),
                     SnapshotOperationsSequence().snapshot_ops_test(), Buckets_operations_sequence().bucket_ops_test(),
                     AutoScalingOperationsSequence().asg_ops_test(), ElasticIPsOperationsSequence().elastic_ip_ops_test()]

        f = open('results.html','w')
        f.write('Started test \n')
        for i in range(1,2):
            test_failed = 0
            print all_tests_capital[i] + " Ops Test"
            print ""
            try:
                print "Executing {0} ops test".format(all_tests_lowercase[i])
                print""
                sequences[i]
            except Exception:
                print "{0} ops test failed".format(all_tests_capital[i])
                test_failed = 1
            if test_failed is 0:
                f.write('{0} ops test PASSED \n'.format(all_tests_capital[i]))
            else:
                f.write('{0} ops test FAILED \n'.format(all_tests_capital[i]))




if __name__ == '__main__':
        tester = Complete_sequence()
        Complete_sequence.run_all_tests(tester)







