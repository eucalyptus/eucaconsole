# Copyright 2015 Hewlett Packard Enterprise Development LP
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import simplejson as json

from pyramid import testing

from eucaconsole.routes import urls


def _register_routes(config):
    for route in urls:
        config.add_route(route.name, route.pattern)


class TestAWSConvert(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_url_for_resource(self):
        from eucaconsole.views.stacks import StackStateView
        _register_routes(self.config)
        request = testing.DummyRequest()
        
        url = StackStateView.get_url_for_resource(request, 'AWS::ElasticLoadBalancing::LoadBalancer', 'lb-1234')
        self.assertEqual(url, '/elbs/lb-1234')

        url = StackStateView.get_url_for_resource(request, 'AWS::EC2::SecurityGroup', 'sg-1234')
        self.assertEqual(url, '/securitygroups/sg-1234')

        url = StackStateView.get_url_for_resource(request, 'AWS::EC2::EIP', '1.2.3.4')
        self.assertEqual(url, '/ipaddresses/1.2.3.4')

        url = StackStateView.get_url_for_resource(request, 'AWS::EC2::Instance', 'i-1234')
        self.assertEqual(url, '/instances/i-1234')

        url = StackStateView.get_url_for_resource(request, 'AWS::EC2::Volume', 'vol-1234')
        self.assertEqual(url, '/volumes/vol-1234')

        url = StackStateView.get_url_for_resource(request, 'AWS::AutoScaling::LaunchConfiguration', 'lc-test')
        self.assertEqual(url, '/launchconfigs/lc-test')

        url = StackStateView.get_url_for_resource(request, 'AWS::AutoScaling::ScalingGroup', 'scalinggroup-test')
        self.assertEqual(url, '/scalinggroups/scalinggroup-test')

        url = StackStateView.get_url_for_resource(request, 'AWS::IAM::Group', 'test-group')
        self.assertEqual(url, '/groups/test-group')

        url = StackStateView.get_url_for_resource(request, 'AWS::IAM::Role', 'test-role')
        self.assertEqual(url, '/roles/test-role')

        url = StackStateView.get_url_for_resource(request, 'AWS::IAM::User', 'test-user')
        self.assertEqual(url, '/users/test-user')

        url = StackStateView.get_url_for_resource(request, 'AWS::S3::Bucket', 'test-bucket')
        self.assertEqual(url, '/buckets/test-bucket/contents/')

    def test_aws_convert(self):
        from eucaconsole.views.stacks import StackWizardView
        # this is an actual aws template that contains RDS resources
        template_file = "tests/stacks/test_template.json"
        template = open(template_file, 'r').read()
        parsed = json.loads(template)
        items = StackWizardView.identify_aws_template(parsed, modify=False)
        # verify items identified
        self.assertTrue(len(items) > 0)
        items = StackWizardView.identify_aws_template(parsed, modify=True)
        # verify items identified, but remove them
        self.assertTrue(len(items) > 0)
        items = StackWizardView.identify_aws_template(parsed, modify=False)
        # verify no more items
        self.assertTrue(len(items) == 0)
