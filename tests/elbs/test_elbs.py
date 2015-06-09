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

from boto.ec2.elb.attributes import LbAttributes, CrossZoneLoadBalancingAttribute

from moto import mock_elb


from eucaconsole.views.elbs import ELBView, ELBMonitoringView, ELBInstancesView, ELBHealthChecksView

from tests import BaseViewTestCase, Mock


class MockELBMixin(object):
    @staticmethod
    @mock_elb
    def make_elb():
        elb_conn = boto.connect_elb('us-east')
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

    def test_normalize_listeners(self):
        listeners = [
            {'input': (80, 80, 'HTTP'), 'output': (80, 80, u'HTTP', u'HTTP')},
            {'input': (80, 80, 'HTTP', 'HTTP'), 'output': (80, 80, u'HTTP', u'HTTP')},
            {'input': (80, 80, u'HTTP', u'HTTP'), 'output': (80, 80, u'HTTP', u'HTTP')},
        ]
        for listener in listeners:
            normalized_listener = ELBView.normalize_listener(listener.get('input'))
            self.assertEqual(normalized_listener, listener.get('output'))


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


class ELBInstancesViewTests(BaseViewTestCase, MockELBMixin):
    """ELB detail page view - Instances tab"""
    def test_elb_instances_tab_view(self):
        elb_conn, elb = self.make_elb()
        request = self.create_request()
        elb_attrs = LbAttributes(connection=elb_conn)
        elb_attrs.cross_zone_load_balancing = CrossZoneLoadBalancingAttribute(connection=elb_conn)
        elb_attrs.cross_zone_load_balancing.enabled = True
        view = ELBInstancesView(request, elb=elb, elb_attrs=elb_attrs).elb_instances()
        options_json = json.loads(view.get('controller_options_json'))
        self.assertEqual(view.get('elb_name'), 'test_elb')
        self.assertEqual(options_json.get('cross_zone_enabled'), True)


class ELBHealthChecksViewTests(BaseViewTestCase, MockELBMixin):
    """ELB detail page view - Health Checks tab"""
    def test_elb_health_checks_tab_view(self):
        elb_conn, elb = self.make_elb()
        health_check = Mock(
            target='HTTP:80/index.html', interval=300, timeout=15, healthy_threshold=3, unhealthy_threshold=5)
        elb.health_check = health_check
        request = self.create_request()
        view = ELBHealthChecksView(request, elb=elb).elb_healthchecks()
        form = view.get('elb_form')
        self.assertEqual(view.get('elb_name'), 'test_elb')
        self.assertEqual(form.ping_protocol.data, 'HTTP')
        self.assertEqual(form.ping_port.data, 80)
        self.assertEqual(form.ping_path.data, 'index.html')
        self.assertEqual(form.passes_until_healthy.data, '3')
        self.assertEqual(form.failures_until_unhealthy.data, '5')
