# -*- coding: utf-8 -*-
# Copyright 2017 Hewlett Packard Enterprise Development LP
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
A connection objects for Eucalyptus Reporting features

"""

import boto
from boto.connection import AWSQueryConnection
from boto.compat import json

from .utils import HttpsConnectionFactory


class EucalyptusConnection(AWSQueryConnection):
    """
    This class contains common code used by both billing/reporting endpoints.
    """

    def __init__(self, ufshost, port, access_id=None, secret_key=None, token=None, path='/'):
        super(EucalyptusConnection, self).__init__(
            access_id, secret_key, host=ufshost,
            port=port, path=path, security_token=token,
            https_connection_factory=(HttpsConnectionFactory(port).https_connection_factory, ())
        )
        self.version = '2016-08-02'

    def _required_auth_capability(self):
        return ['hmac-v4']

    # stolen from boto.cloudformat.connection
    def _do_request(self, call, params, method):
        """
        Do a request via ``self.make_request`` and parse the JSON response.

        :type call: string
        :param call: Call name, e.g. ``CreateStack``

        :type params: dict
        :param params: Dictionary of call parameters

        :type path: string
        :param path: Server path

        :type method: string
        :param method: HTTP method to use

        :rtype: dict
        :return: Parsed JSON response data
        """
        params['Version'] = self.version
        response = self.make_request(call, params, self.path, method)
        body = response.read().decode('utf-8')
        if response.status == 200:
            body = json.loads(body)
            return body
        else:
            boto.log.error('%s %s' % (response.status, response.reason))
            boto.log.error('%s' % body)
            raise self.ResponseError(response.status, response.reason, body=body)


class EucalyptusReporting(EucalyptusConnection):
    """
    This class contains methods to access API calls against the Portal endpoint
    """

    def __init__(self, ufshost, port, access_id=None, secret_key=None, token=None, dns_enabled=True):
        if dns_enabled:
            ufshost = 'portal.{0}'.format(ufshost)
        path = '/services/Portal'
        super(EucalyptusReporting, self).__init__(
            ufshost, port, access_id=access_id, secret_key=secret_key, token=token, path=path
        )

    def view_account(self):
        """
        implements ViewAccount
        """
        params = {}
        ret = self._do_request('ViewAccount', params, 'POST')
        return ret

    def modify_account(self, user_billing_access_enabled):
        """
        implements ModifyAccount
        """
        params = {
            'UserBillingAccess': user_billing_access_enabled
        }
        ret = self._do_request('ModifyAccount', params, 'POST')
        return ret

    def view_billing(self):
        """
        implements ViewBilling
        """
        params = {}
        ret = self._do_request('ViewBilling', params, 'POST')
        return ret

    def modify_billing(self, enabled, bucket_name, cost_allocation_tags=[]):
        """
        implements ModifyBilling
        """
        params = {
            'DetailedBillingEnabled': enabled,
            'ReportBucket': bucket_name
        }
        if len(cost_allocation_tags) > 0:
            for i, tag in enumerate(cost_allocation_tags):
                params['ActiveCostAllocationTags.%d' % (i + 1)] = tag
        ret = self._do_request('ModifyBilling', params, 'POST')
        return ret

    def view_monthly_usage(self, year, month):
        """
        implements ViewMonthlyUsage
        """
        params = {
            'Year': year,
            'Month': month
        }
        ret = self._do_request('ViewMonthlyUsage', params, 'POST')
        return ret

    def view_usage(self, service, usage_types, operations, start_time, end_time, report_granularity='Hours'):
        """
        implements ViewUsage
        """
        params = {
            'Services': service,
            'UsageTypes': usage_types,
            'Operations': operations,
            'TimePeriodFrom': start_time.isoformat(),
            'TimePeriodTo': end_time.isoformat(),
            'ReportGranularity': report_granularity
        }
        ret = self._do_request('ViewUsage', params, 'POST')
        return ret


class EucalyptusEC2Reports(EucalyptusConnection):
    """
    This class contains methods to access API calls against the EC2Reports endpoint
    """

    def __init__(self, ufshost, port, access_id=None, secret_key=None, token=None, dns_enabled=True):
        if dns_enabled:
            ufshost = 'ec2reports.{0}'.format(ufshost)
        path = '/services/Ec2Reports'
        super(EucalyptusEC2Reports, self).__init__(
            ufshost, port, access_id=access_id, secret_key=secret_key, token=token, path=path
        )

    def view_instance_usage_report(self, start_time, end_time, filters, group_by, report_granularity='Daily'):
        """
        implements ViewUsage
        """
        params = {
            'Granularity': report_granularity,
            'TimeRangeStart': start_time.isoformat(),
            'TimeRangeEnd': end_time.isoformat(),
        #    'GroupBy.Type': group_by,
        #    'GroupBy.Key': group_by,
        }
        if len(filters) > 0:
            for i, f in enumerate(filters):
                params['Filters.member.%d.Type' % (i + 1)] = f.get('type')
                params['Filters.member.%d.Key' % (i + 1)] = f.get('key')
        ret = self._do_request('ViewInstanceUsageReport', params, 'POST')
        return ret

