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
Authentication and Authorization models

"""
import base64
import httplib
import pylibmc
import socket
import urllib2
from urlparse import urlparse

from defusedxml.sax import parseString
from ssl import SSLError

from boto import ec2
from boto import vpc
from boto.https_connection import CertValidatingHTTPSConnection
from boto.ec2.connection import EC2Connection
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat
# uncomment to enable boto request logger. Use only for development (see ref in _euca_connection)
# from boto.requestlog import RequestLogger
import boto
import boto.ec2.autoscale
import boto.cloudformation
import boto.ec2.cloudwatch
import boto.ec2.elb
import boto.iam
from boto.handler import XmlHandler as BotoXmlHandler
from boto.regioninfo import RegionInfo
from boto.sts.credentials import Credentials
from pyramid.security import Authenticated, authenticated_userid
from .admin import EucalyptusAdmin
from ..caches import default_term


class User(object):
    """Authenticated/Anonymous User object for Pyramid Auth."""
    def __init__(self, user_id=None):
        self.user_id = user_id

    @classmethod
    def get_auth_user(cls, request):
        """Get an authenticated user.  Note that self.user_id = None if not authenticated.
           See: http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/auth/user_object.html
        """
        user_id = authenticated_userid(request)
        return cls(user_id=user_id)

    def is_authenticated(self):
        """user_id will be None if the user isn't authenticated"""
        return self.user_id

    @staticmethod
    def get_account_id(ec2_conn=None, request=None):
        """Get 12-digit account ID for the currently signed-in user's account using the default security group"""
        from ..views import boto_error_handler
        account_id = ""
        if ec2_conn and request:
            with boto_error_handler(request):
                security_groups = ec2_conn.get_all_security_groups(filters={'group-name': 'default'})
                security_group = security_groups[0] if security_groups else None 
                if security_group is not None:
                    account_id = security_group.owner_id
        return account_id
                    

class RegionCache(object):
    """ Returns cached list of regions for current cloud"""
    def __init__(self, conn=None):
        self.conn = conn

    # TODO: provide cache invalidating method?

    def regions(self, regions=None):
        """Returns a list of region choices. Will fetch regions if not passed"""
        choices = []
        regions = regions or []
        if not regions:
            regions.extend(self.get_regions(self.conn.host if self.conn else None))
        for region in regions:
            choices.append(dict(
                name=region.name,
                label=region.name,
                endpoints=dict(
                    ec2=region.endpoint
                )
            ))
        return sorted(choices)

    def get_regions(self, host):
        @default_term.cache_on_arguments(namespace='regions')
        def _get_regions_cache_(self, host):
            return _get_regions_(self)

        def _get_regions_(self):
            regions = []
            if self.conn is not None:
                regions = self.conn.get_all_regions()
            return regions
        try:
            return _get_regions_cache_(self, host)
        except pylibmc.Error:
            return _get_regions_(self)


class ConnectionManager(object):
    """Returns connection objects, pulling from Beaker cache when available"""
    @staticmethod
    def aws_connection(region, access_key, secret_key, token, conn_type, validate_certs=False):
        """Return AWS EC2 connection object
        Pulls from Beaker cache on subsequent calls to avoid connection overhead

        :type region: string
        :param region: region name (e.g. 'us-east-1')

        :type access_key: string
        :param access_key: AWS access key

        :type secret_key: string
        :param secret_key: AWS secret key

        :type conn_type: string
        :param conn_type: Connection type ('ec2', 'autoscale', 'cloudwatch', 'cloudformation', 'elb', or 's3')

        :type validate_certs: bool
        :param validate_certs: indicates to check the ssl cert the server provides

        """

        def _aws_connection(_region, _access_key, _secret_key, _token, _conn_type):
            conn = None
            if conn_type == 'ec2':
                conn = ec2.connect_to_region(
                    _region, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 'autoscale':
                conn = ec2.autoscale.connect_to_region(
                    _region, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 'cloudwatch':
                conn = ec2.cloudwatch.connect_to_region(
                    _region, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 'cloudformation':
                conn = boto.cloudformation.connect_to_region(
                    _region, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 's3':
                conn = boto.connect_s3(  # Don't specify region when connecting to S3
                    aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 'elb':
                conn = ec2.elb.connect_to_region(
                    _region, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 'vpc':
                conn = vpc.connect_to_region(
                    _region, aws_access_key_id=_access_key, aws_secret_access_key=_secret_key, security_token=_token)
            elif conn_type == 'iam':
                return None
            if conn:
                conn.https_validate_certificates = validate_certs
            return conn

        return _aws_connection(region, access_key, secret_key, token, conn_type)

    @staticmethod
    def euca_connection(ufshost, port, region, access_id, secret_key, token, conn_type,
                        dns_enabled=True, validate_certs=False, certs_file=None):
        """Return Eucalyptus connection object

        :type ufshost: string
        :param ufshost: FQDN or IP of Eucalyptus UFS host (for user facing services)

        :type port: int
        :param port: Port of Eucalyptus CLC (usually 8773)

        :type access_id: string
        :param access_id: Euca access id

        :type secret_key: string
        :param secret_key: Eucalyptus secret key

        :type conn_type: string
        :param conn_type: Connection type ('ec2', 'autoscale', 'cloudwatch', 'cloudformation', 'elb',
                                           'iam', 'sts', or 's3')

        :type dns_enabled: boolean
        :param dns_enabled: True if dns enabled for cloud we're connecting to

        :type validate_certs: bool
        :param validate_certs: indicates to check the ssl cert the server provides

        :type certs_file: string
        :param certs_file: indicates the location of the certificates file, if otherthan standard

        """
        def _euca_connection(_ufshost, _port, _region, _access_id, _secret_key, _token, _conn_type, _dns_enabled):
            path = 'compute'
            conn_class = EC2Connection
            api_version = '2012-12-01'
            if _region != 'euca':
                # look up region endpoint
                conn = _euca_connection(
                    _ufshost, _port, 'euca', _access_id, _secret_key, _token, 'ec2', _dns_enabled
                )
                regions = RegionCache(conn).get_regions(_ufshost)
                region = [region.endpoint for region in regions if region.name == _region]
                if region:
                    endpoint = region[0]
                    parsed = urlparse(endpoint)
                    _ufshost = parsed.hostname[4:]  # remove 'ec2.' prefix
                    _port = parsed.port

            # special case since this is our own class, not boto's
            if _conn_type == 'admin':
                return EucalyptusAdmin(_ufshost, _port, _access_id, _secret_key, _token, _dns_enabled)

            # Configure based on connection type
            if _conn_type == 'autoscale':
                api_version = '2011-01-01'
                conn_class = boto.ec2.autoscale.AutoScaleConnection
                path = 'AutoScaling'
            elif _conn_type == 'cloudwatch':
                path = 'CloudWatch'
                conn_class = boto.ec2.cloudwatch.CloudWatchConnection
            elif _conn_type == 'cloudformation':
                path = 'CloudFormation'
                conn_class = boto.cloudformation.CloudFormationConnection
            elif _conn_type == 'elb':
                path = 'LoadBalancing'
                conn_class = boto.ec2.elb.ELBConnection
            elif _conn_type == 'iam':
                path = 'Euare'
                conn_class = boto.iam.IAMConnection
            elif _conn_type == 's3':
                path = 'objectstorage'
                conn_class = S3Connection
            elif _conn_type == 'vpc':
                conn_class = boto.vpc.VPCConnection

            if _dns_enabled:
                _ufshost = "{0}.{1}".format(path.lower(), _ufshost)
                path = '/'
            else:
                path = '/services/{0}/'.format(path)
            region = RegionInfo(name='eucalyptus', endpoint=_ufshost)
            # IAM and S3 connections need host instead of region info
            if _conn_type in ['iam', 's3']:
                conn = conn_class(
                    _access_id, _secret_key, host=_ufshost, port=_port, path=path, is_secure=True, security_token=_token
                )
            else:
                conn = conn_class(
                    _access_id, _secret_key, region=region, port=_port, path=path, is_secure=True, security_token=_token
                )
            if _conn_type == 's3':
                conn.calling_format = OrdinaryCallingFormat()

            # AutoScaling service needs additional auth info
            if _conn_type == 'autoscale':
                conn.auth_region_name = 'Eucalyptus'

            setattr(conn, 'APIVersion', api_version)
            if conn:
                conn.https_validate_certificates = validate_certs
            if certs_file is not None:
                conn.ca_certificates_file = certs_file
            conn.http_connection_kwargs['timeout'] = 30
            # uncomment to enable boto request logger. Use only for development
            # conn.set_request_hook(RequestLogger())
            return conn

        return _euca_connection(ufshost, port, region, access_id, secret_key, token, conn_type, dns_enabled)


def groupfinder(user_id, request):
    if user_id is not None:
        return [Authenticated]
    return []


class EucaAuthenticator(object):
    """Eucalyptus cloud token authenticator"""
    # TEMPLATE = '/services/Tokens?Action=GetAccessToken&DurationSeconds={dur}&Version=2011-06-15'
    NON_DNS_QUERY_PATH = '/services/Tokens'
    TEMPLATE = '?Action=GetAccessToken&DurationSeconds={dur}&Version=2011-06-15'

    def __init__(self, host, port, dns_enabled=True, validate_certs=False, **validate_kwargs):
        """
        Configure connection to Eucalyptus STS service to authenticate with the CLC (cloud controller)

        :type host: string
        :param host: IP address or FQDN of CLC host

        :type port: integer
        :param port: port number to use when making the connection

        :type dns_enabled: boolean
        :param dns_enabled: if true, prefix host with tokens., otherwise use request path method

        """
        self.dns_enabled = dns_enabled
        self.host = host
        self.port = port
        self.validate_certs = validate_certs
        self.kwargs = validate_kwargs

    def authenticate(self, account, user, passwd, new_passwd=None, timeout=15, duration=3600):
        # try authentication with default of dns_enabled = True. Set to False if we fail
        # and if that also fails, let that error raise up
        try:
            return self._authenticate_(account, user, passwd, new_passwd, timeout, duration)
        except urllib2.URLError as err:
            # handle case where dns attempt was good, but user unauthorized
            error_msg = getattr(err, 'msg', None)
            if error_msg and error_msg == 'Unauthorized' or error_msg == 'Forbidden':
                raise err
            elif getattr(err, 'reason', '').find('SSL') > -1:
                raise err
            self.dns_enabled = False
            return self._authenticate_(account, user, passwd, new_passwd, timeout, duration)

    def _authenticate_(self, account, user, passwd, new_passwd=None, timeout=15, duration=3600):
        if user == 'admin' and duration > 3600:  # admin cannot have more than 1 hour duration
            duration = 3600
        # because of the variability, we need to keep this here, not in __init__
        auth_path = self.TEMPLATE.format(dur=duration)
        if not self.dns_enabled:
            auth_path = self.NON_DNS_QUERY_PATH + auth_path
        else:
            auth_path = '/' + auth_path
        host = self.host
        if self.dns_enabled:
            host = 'tokens.{0}'.format(host)
        if self.validate_certs:
            conn = CertValidatingHTTPSConnection(host, self.port, timeout=timeout, **self.kwargs)
        else:
            conn = httplib.HTTPSConnection(host, self.port, timeout=timeout)

        if new_passwd:
            auth_string = u"{user}@{account};{pw}@{new_pw}".format(
                user=base64.b64encode(user),
                account=base64.b64encode(account),
                pw=base64.b64encode(passwd),
                new_pw=new_passwd
            )
        else:
            auth_string = u"{user}@{account}:{pw}".format(
                user=base64.b64encode(user),
                account=base64.b64encode(account),
                pw=passwd
            )
        encoded_auth = base64.b64encode(auth_string)
        headers = {'Authorization': "Basic %s" % encoded_auth}
        try:
            conn.request('GET', auth_path, '', headers)
            response = conn.getresponse()
            if response.status != 200:
                raise urllib2.HTTPError(url='', code=response.status, msg=response.reason, hdrs=None, fp=None)
            body = response.read()

            # parse AccessKeyId, SecretAccessKey and SessionToken
            creds = Credentials()
            h = BotoXmlHandler(creds, None)
            parseString(body, h)
            return creds
        except SSLError as err:
            if err.message != '':
                raise urllib2.URLError(str(err))
            else:
                raise urllib2.URLError(err[1])
        except socket.error as err:
            # when dns enabled, but path cloud, we get here with
            # err=gaierror(8, 'nodename nor servname provided, or not known')
            # when dns disabled, but path cloud, we get here with
            # err=gaierror(8, 'nodename nor servname provided, or not known')
            raise urllib2.URLError(str(err))


class AWSAuthenticator(object):

    def __init__(self, package, validate_certs=False, **validate_kwargs):
        """
        Configure connection to AWS STS service

        :type package: string
        :param package: a pre-signed request string for the STS GetSessionToken call

        """
        self.host = 'sts.amazonaws.com'
        self.port = 443
        self.package = package
        self.validate_certs = validate_certs
        self.kwargs = validate_kwargs

    def authenticate(self, timeout=20):
        """ Make authentication request to AWS STS service
            Timeout defaults to 20 seconds"""
        if self.validate_certs:
            conn = CertValidatingHTTPSConnection(self.host, self.port, timeout=timeout, **self.kwargs)
        else:
            conn = httplib.HTTPSConnection(self.host, self.port, timeout=timeout)

        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            conn.request('POST', '', self.package, headers)
            response = conn.getresponse()
            if response.status != 200:
                raise urllib2.HTTPError(url='', code=response.status, msg=response.reason, hdrs=None, fp=None)
            body = response.read()
            
            # parse AccessKeyId, SecretAccessKey and SessionToken
            creds = Credentials()
            h = BotoXmlHandler(creds, None)
            parseString(body, h)
            return creds
        except SSLError as err:
            if err.message != '':
                raise urllib2.URLError(err.message)
            else:
                raise urllib2.URLError(err[1])
        except socket.error as err:
            raise urllib2.URLError(err.message)
