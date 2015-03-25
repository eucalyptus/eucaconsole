import unittest
from guiops.tests.login import LoginTest
from guiops.tests.dashboard import DashboardTests

def LoginTestcase(BaseTezt):
    test_keypair_works
euca_login=unittest.TestSuite.addTest(LoginTest,LoginTest.test_euca_login())

euca_navigation=unittest.TestSuite.addTest(DashboardTests,DashboardTests.test_from_dashboard_goto_keypairs_lp_via_icon())

smoke_tests = unittest.TestSuite([euca_login,euca_navigation])

unittest.TextTestRunner(verbosity=2).run(smoke_tests)