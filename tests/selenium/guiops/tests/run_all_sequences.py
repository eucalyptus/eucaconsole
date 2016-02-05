from guiops.guiops import GuiOps
from option_parser import Option_parser
from keypair import Keypair_operations_sequence
from security_groups import Security_group_operations_sequence
from instances import Instance_operations_sequence
from volumes import VolumeOperationsSequence
from snapshots import Snapshot_operations_sequence
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
        f = open('results.html','w')
        f.write('Started test \n')
        test_failed = 0
        print "KEYPAIR OPS TEST"
        print ""
        try:
            print "Executing keypair ops test"
            print""
            Keypair_operations_sequence().keypair_ops_test()
        except Exception:
            print "Keypair ops test failed"
            test_failed = 1
        if test_failed is 0:
            f.write('KEYPAIR OPS TEST PASSED \n')
        else:
            f.write('KEYPAIR OPS TEST FAILED \n')
        test_failed = 0
        print "SECURITY GROUP OPS TEST"
        print ""
        try:
            print "Executing security group ops test"
            print""
            Security_group_operations_sequence().security_group_ops_test()
        except Exception:
            test_failed = 1
            print "Security group ops test failed"
        if test_failed is 0:
            f.write('SECURITY GROUP OPS TEST PASSED \n')
        else:
            f.write('SECURITY GROUP OPS TEST FAILED \n')
        test_failed = 0
        print "INSTANCE OPS TEST"
        print ""
        try:
            print "Executing instance ops test"
            print""
            Instance_operations_sequence().instance_ops_test()
        except Exception:
            test_failed = 1
            print "Instance ops test failed"
        if test_failed is 0:
            f.write('INSTANCE OPS TEST PASSED \n')
        else:
            f.write('INSTANCE OPS TEST FAILED \n')
        test_failed = 0
        print "VOLUME OPS TEST"
        print ""
        try:
            print "Executing volume ops test"
            print""
            VolumeOperationsSequence().volume_ops_test()
        except Exception:
            test_failed = 1
            print "Volume ops test failed"
        if test_failed is 0:
            f.write('VOLUME OPS TEST PASSED \n')
        else:
            f.write('VOLUME OPS TEST FAILED \n')
        test_failed = 0
        print "SNAPSHOT OPS TEST"
        print ""
        try:
            print "Executing snapshot ops test"
            print""
            Snapshot_operations_sequence().snapshot_ops_test()
        except Exception:
            test_failed = 1
            print "Snapshot ops test failed"
        test_failed = 0
        print "BUCKET OPS TEST"
        print ""
        try:
            print "Executing bucket ops test"
            print""
            Buckets_operations_sequence().bucket_ops_test()
        except Exception:
            test_failed = 1
            print "Bucket ops test failed"
        test_failed = 0
        print "AUTOSCALING OPS TEST"
        print ""
        try:
            print "Autoscaling ops test"
            print""
            AutoScalingOperationsSequence().asg_ops_test()
        except Exception:
            test_failed = 1
            print "Autoscaling ops test failed"
        test_failed = 0
        print "ELASTIC IPS OPS TEST"
        print ""
        try:
            print "Elastic IP ops test"
            print""
            ElasticIPsOperationsSequence().elastic_ip_ops_test()
        except Exception:
            test_failed = 1
            print "Elastic IP ops test failed"
        f.close()


if __name__ == '__main__':
        tester = Complete_sequence()
        Complete_sequence.run_all_tests(tester)







