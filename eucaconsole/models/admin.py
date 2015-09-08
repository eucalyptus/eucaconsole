# -*- coding: utf-8 -*-
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
A connection object for Eucalyptus Admin features

"""

from boto.connection import AWSQueryConnection
from boto.resultset import ResultSet


class Service(object):
    """
    Represents an Eucalyptus service
    """
    def __init__(self, connection=None):
        super(Service, self).__init__()
        self.name = None
        self.partition = None
        self.service_type = None
        self.full_name = None
        self.uris = None
        self.uri = None
        self.host = None
        self.state = None
        self.epoch = None
        self.accounts = None

    def __repr__(self):
        return 'Service:%s' % self.name

    def startElement(self, name, attrs, connection):
        if name == 'euca:uris':
            self.uris = ResultSet([('euca:item', Uri)])
            return self.uris
        elif name == 'euca:serviceAccounts':
            self.accounts = ResultSet([('euca:item', ServiceAccount)])
            return self.accounts

    def endElement(self, name, value, connection):
        if name == 'euca:partition':
            self.partition = value
        elif name == 'euca:name':
            self.name = value
        elif name == 'euca:type':
            self.service_type = value
        elif name == 'euca:fullName':
            self.full_name = value
        elif name == 'euca:uri':
            self.uri = value
        elif name == 'euca:host':
            self.host = value
        elif name == 'euca:localState':
            self.state = value
        elif name == 'euca:localEpoch':
            self.epoch = value
        else:
            setattr(self, name, value)


class Uri(object):
    """
    Represents uri info for a service
    """
    def __init__(self, connection=None):
        self.entry = None

    def __repr__(self):
        return 'Uri:%s' % self.entry

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'euca:entry':
            self.entry = value


class ServiceAccount(object):
    """
    Represents account info for a service
    """
    def __init__(self, connection=None):
        self.account_name = None
        self.account_number = None
        self.account_canonical_id = None

    def __repr__(self):
        return 'Account:%s' % self.account_name

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'euca:accountName':
            self.account_name = value
        elif name == 'euca:accountNumber':
            self.account_number = value
        elif name == 'euca:accountCanonicalId':
            self.account_canonical_id = value


class EucalyptusAdmin(AWSQueryConnection):

    def __init__(self, ufshost, port, access_id=None, secret_key=None, token=None, dns_enabled=True):
        self.version = 'eucalyptus'
        if dns_enabled:
            ufshost = 'bootstrap.{0}'.format(ufshost)
        path = '/services/Empyrean'
        super(AWSQueryConnection, self).__init__(
            ufshost, access_id, secret_key,
            is_secure=False, port=port,
            path=path, security_token=token
        )

    def get_all_services(self, service_type=None):
        """
        results like empyrian-describe-services
        """
        params = {}
        if service_type:
            params['ByServiceType'] = service_type
        params['Version'] = self.version
        old_auth = self._auth_handler
        ret = self.get_list('DescribeServices', params, [('euca:item', Service)])
        self._auth_handler = old_auth
        return ret

