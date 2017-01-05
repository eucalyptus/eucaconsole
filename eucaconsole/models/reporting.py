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
A connection object for Eucalyptus Reporting features

"""

import httplib
import logging
import ssl

import boto
from boto.connection import AWSQueryConnection
from boto.resultset import ResultSet
from boto.compat import json


class HttpsConnectionFactory(object):
    def __init__(self, port):
        self.port = port

    def https_connection_factory(self, host, **kwargs):
        """Returns HTTPS connection object with appropriate SSL context
        :param host:

        NOTE: Python < 2.7.9 is missing the ssl._create_unverified_context
              and doesn't accept a 'context' kwarg in httplib.HTTPSConnection
        """
        if hasattr(ssl, '_create_unverified_context'):
            kwargs.update(context=ssl._create_unverified_context())
        return httplib.HTTPSConnection(host, port=self.port, **kwargs)


class EucalyptusReporting(AWSQueryConnection):

    def __init__(self, ufshost, port, access_id=None, secret_key=None, token=None, dns_enabled=True):
        self.version = '2016-08-02'
        if dns_enabled:
            ufshost = 'portal.{0}'.format(ufshost)
        path = '/services/Portal'
        super(AWSQueryConnection, self).__init__(
            ufshost, access_id, secret_key,
            is_secure=True, port=port,
            path=path, security_token=token,
            https_connection_factory=(HttpsConnectionFactory(port).https_connection_factory, ())
        )

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
        
    def view_billing(self):
        """
        implements ViewBilling
        """
        params = {}
        ret = self._do_request('ViewBilling', params, 'POST')
        return ret

    def modify_billing(self, enabled, bucket_name, cost_allocation_tags=[]):
        """
        implements ViewBilling
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


