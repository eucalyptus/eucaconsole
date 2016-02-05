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

        print "KEYPAIR OPS TEST"
        print ""
        try:
            print "Executing keypair ops test"
            print""
            Keypair_operations_sequence().keypair_ops_test()
        except Exception:
            print "Keypair ops test failed"
        print "SECURITY GROUP OPS TEST"
        print ""
        try:
            print "Executing security group ops test"
            print""
            Security_group_operations_sequence().security_group_ops_test()
        except Exception:
            print "Security group ops test failed"
        print "INSTANCE OPS TEST"
        print ""
        try:
            print "Executing instance ops test"
            print""
            Instance_operations_sequence().instance_ops_test()
        except Exception:
            print "Instance ops test failed"
        print "VOLUME OPS TEST"
        print ""
        try:
            print "Executing volume ops test"
            print""
            VolumeOperationsSequence().volume_ops_test()
        except Exception:
            print "Volume ops test failed"
        print "SNAPSHOT OPS TEST"
        print ""
        #Snapshot_operations_sequence().snapshot_ops_test()
        print "BUCKET OPS TEST"
        print ""
        try:
            print "Executing bucket ops test"
            print""
            Buckets_operations_sequence().bucket_ops_test()
        except Exception:
            print "Bucket ops test failed"

        print "AUTOSCALING OPS TEST"
        print ""
        #AutoScalingOperationsSequence().asg_ops_test()
        print "ELASTIC IPS OPS TEST"
        print ""
        #ElasticIPsOperationsSequence().elastic_ip_ops_test()




if __name__ == '__main__':
        tester = Complete_sequence()
        Complete_sequence.run_all_tests(tester)







