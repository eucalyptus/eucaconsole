# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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

from moto import mock_elb, mock_cloudwatch


from eucaconsole.i18n import _
from eucaconsole.constants.elbs import ELB_EMPTY_DATA_MESSAGE
from eucaconsole.forms.elbs import ELBForm, ELBHealthChecksForm
from eucaconsole.views.elbs import ELBsJsonView, ELBView, ELBMonitoringView, ELBInstancesView, ELBHealthChecksView

from tests import BaseViewTestCase, BaseFormTestCase, Mock


class MockELBMixin(object):
    @staticmethod
    @mock_elb
    def make_elb():
        elb_conn = boto.connect_elb()
        name = 'test_elb'
        zones = ['us-east-1a']
        listeners = [(80, 80, 'HTTP', 'HTTP')]
        elb = elb_conn.create_load_balancer(name, zones, complex_listeners=listeners)
        elb.idle_timeout = 60
        return elb_conn, elb

    @staticmethod
    @mock_cloudwatch
    def make_cw_conn():
        return boto.connect_cloudwatch()


class ELBLandingPageJsonViewTests(BaseViewTestCase, MockELBMixin):
    @mock_elb
    def test_elb_landing_page_json_view(self):
        elb_conn, elb = self.make_elb()
        cw_conn = self.make_cw_conn()
        request = self.create_request()
        view = ELBsJsonView(request, elb_conn=elb_conn, cw_conn=cw_conn, elb=elb).elbs_json()
        results = view.get('results')
        elb = results[0]
        self.assertEqual(len(results), 1)
        self.assertEqual(elb.get('healthy_hosts'), 0)
        self.assertEqual(elb.get('unhealthy_hosts'), 0)


class ELBViewTests(BaseViewTestCase, MockELBMixin):
    """ELB detail page view - General tab"""
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
        chart_help = _(
            'The total number of completed requests that were received and routed to the registered instances. '
            'Defaults to the sum statistic for the best output results.')
        chart_item = {
            "metric": "RequestCount", "unit": "Count", "statistic": "Sum", "empty_msg": ELB_EMPTY_DATA_MESSAGE,
            "help": chart_help
        }
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


class ELBDetailPageFormTests(BaseFormTestCase, BaseViewTestCase, MockELBMixin):
    @mock_elb
    def test_elb_detail_page_form(self):
        request = self.create_request()
        elb_conn, elb = self.make_elb()
        elb.idle_timeout = 30
        form = ELBForm(request, elb_conn=elb_conn, elb=elb)
        self.assertEqual(form.get_idle_timeout(elb), 30)
        self.assertEqual(form.idle_timeout.data, 30)
        self.assertEqual(form.logging_enabled.data, False)
        self.assertEqual(form.bucket_name.data, None)
        self.assertEqual(form.bucket_prefix.data, None)
        self.assertEqual(form.collection_interval.data, '60')


class ELBHealthChecksFormTests(BaseFormTestCase, BaseViewTestCase, MockELBMixin):
    @mock_elb
    def test_elb_health_checks_form(self):
        request = self.create_request()
        elb_conn, elb = self.make_elb()
        elb.health_check = Mock(
            interval=30,
            timeout=30,
            healthy_threshold=3,
            unhealthy_threshold=2,
            target='HTTP:80/index.html',
        )
        form = ELBHealthChecksForm(request, elb_conn=elb_conn, elb=elb)
        self.assertEqual(form.ping_protocol.data, 'HTTP')
        self.assertEqual(form.ping_port.data, 80)
        self.assertEqual(form.ping_path.data, 'index.html')
        self.assertEqual(form.time_between_pings.data, '30')
        self.assertEqual(form.response_timeout.data, 30)
        self.assertEqual(form.failures_until_unhealthy.data, '2')
        self.assertEqual(form.passes_until_healthy.data, '3')
