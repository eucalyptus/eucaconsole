import unittest
from guiops.tests.login import LoginTest
from guiops.tests.navigation import *

#euca_navigation=unittest.TestLoader().loadTestsFromTestCase(Navigation_sequence_run)

euca_login=unittest.TestLoader().loadTestsFromTestCase(LoginTest)

smoke_tests = unittest.TestSuite([euca_login])

unittest.TextTestRunner(verbosity=2).run(smoke_tests)