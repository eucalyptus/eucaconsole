# Copyright 2013-2014 Eucalyptus Systems, Inc.
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

"""
ELB tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
import json

import boto

from moto import mock_elb


from eucaconsole.views.elbs import ELBView, ELBMonitoringView

from tests import BaseViewTestCase


class MockELBMixin(object):
    @staticmethod
    @mock_elb
    def make_elb():
        elb_conn = boto.connect_elb('us-east')
        # params = dict(complex_listeners=listeners_args)
        name = 'test_elb'
        zones = ['us-east-1a']
        listeners = [(80, 80, 'HTTP', 'HTTP')]
        elb = elb_conn.create_load_balancer(name, zones, complex_listeners=listeners)
        elb.idle_timeout = 60
        return elb_conn, elb


class ELBViewTests(BaseViewTestCase, MockELBMixin):
    """ELB detail page view - General tab"""
    def test_elb_general_tab_view(self):
        elb_conn, elb = self.make_elb()
        request = self.create_request()
        elb_tags = {'foo': 'bar'}
        view = ELBView(request, elb_conn=elb_conn, elb=elb, elb_tags=elb_tags).elb_view()
        self.assertEqual(view.get('elb_name'), 'test_elb')
        self.assertEqual(view.get('elb_tags'), 'foo=bar')
        self.assert_({'name': 'HTTP', 'port': '80', 'value': 'HTTP'} in view.get('protocol_list'))


class ELBMonitoringViewTests(BaseViewTestCase, MockELBMixin):
    """ELB detail page view - Monitoring tab"""
    def test_elb_monitoring_tab_view(self):
        elb_conn, elb = self.make_elb()
        request = self.create_request()
        view = ELBMonitoringView(request, elb=elb).elb_monitoring()
        options_json = json.loads(view.get('controller_options_json'))
        chart_item = {"metric": "RequestCount", "unit": "Count", "statistic": "Sum"}
        self.assertEqual(view.get('elb_name'), 'test_elb')
        self.assert_(chart_item in options_json.get('charts_list'))
