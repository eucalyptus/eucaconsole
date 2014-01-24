# -*- coding: utf-8 -*-
"""
Authentication and Authorization models

"""
import base64
import hashlib
import hmac
import logging
import urllib
import urllib2
import urlparse
import xml

from datetime import datetime

from beaker.cache import cache_region
from boto import ec2
from boto.ec2.connection import EC2Connection
import boto.ec2.autoscale
import boto.ec2.cloudwatch
import boto.ec2.elb
import boto.iam
from boto.handler import XmlHandler as BotoXmlHandler
from boto.regioninfo import RegionInfo
from boto.sts.credentials import Credentials
from pyramid.security import Authenticated, authenticated_userid


class User(object):
    """Authenticated/Anonymous User object for Pyramid Auth.
       Note: This is not an IAM User object (maybe not yet anyway)
    """
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


class ConnectionManager(object):
    """Returns connection objects, pulling from Beaker cache when available"""
    @staticmethod
    @cache_region('default_term', 'aws_connection_cache')
    def aws_connection(region, access_key, secret_key, token, conn_type):
        """Return AWS EC2 connection object
        Pulls from Beaker cache on subsequent calls to avoid connection overhead

        :type region: string
        :param region: region name (e.g. 'us-east-1')

        :type access_key: string
        :param access_key: AWS access key

        :type secret_key: string
        :param secret_key: AWS secret key

        :type conn_type: string
        :param conn_type: Connection type ('ec2', 'autoscale', 'cloudwatch', or 'elb')

        """
        conn = None
        if conn_type == 'ec2':
            conn = ec2.connect_to_region(
                region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, security_token=token)
        elif conn_type == 'autoscale':
            conn = ec2.autoscale.connect_to_region(
                region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, security_token=token)
        elif conn_type == 'cloudwatch':
            conn = ec2.cloudwatch.connect_to_region(
                region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, security_token=token)
        if conn_type == 'elb':
            conn = ec2.elb.connect_to_region(
                region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, security_token=token)
        return conn

    @staticmethod
    @cache_region('default_term', 'euca_connection_cache')
    def euca_connection(clchost, port, access_id, secret_key, token, conn_type):
        """Return Eucalyptus connection object
        Pulls from Beaker cache on subsequent calls to avoid connection overhead

        :type clchost: string
        :param clchost: FQDN or IP of Eucalyptus CLC (cloud controller)

        :type port: int
        :param port: Port of Eucalyptus CLC (usually 8773)

        :type access_id: string
        :param access_id: Euca access id

        :type secret_key: string
        :param secret_key: Eucalyptus secret key

        :type conn_type: string
        :param conn_type: Connection type ('ec2', 'autoscale', 'cloudwatch', or 'elb')

        """
        region = RegionInfo(name='eucalyptus', endpoint=clchost)
        path = '/services/Eucalyptus'
        conn_class = EC2Connection
        api_version = '2012-12-01'

        # Configure based on connection type
        if conn_type == 'autoscale':
            api_version = '2011-01-01'
            conn_class = boto.ec2.autoscale.AutoScaleConnection
            path = '/services/AutoScaling'
        if conn_type == 'cloudwatch':
            path = '/services/CloudWatch'
            conn_class = boto.ec2.cloudwatch.CloudWatchConnection
        if conn_type == 'elb':
            path = '/services/LoadBalancing'
            conn_class = boto.ec2.elb.ELBConnection
        if conn_type == 'iam':
            path = '/services/Euare'
            conn_class = boto.iam.IAMConnection

        if conn_type != 'iam':
            conn = conn_class(
                access_id, secret_key, region=region, port=port, path=path, is_secure=True, security_token=token)
        else:
            conn = conn_class(
                access_id, secret_key, host=clchost, port=port, path=path, is_secure=True, security_token=token)

        # AutoScaling service needs additional auth info
        if conn_type == 'autoscale':
            conn.auth_region_name = 'Eucalyptus'

        setattr(conn, 'APIVersion', api_version)
        conn.https_validate_certificates = False
        conn.http_connection_kwargs['timeout'] = 30
        return conn


def groupfinder(user_id, request):
    if user_id is not None:
        return [Authenticated]
    return []


class AWSQuery(object):
    """
    Build a signed request to an Amazon AWS endpoint.
    Credit: https://github.com/kesor/amazon-queries

    :type endpoint: string
    :param endpoint: from http://docs.amazonwebservices.com/general/latest/gr/rande.html

    :type key_id: string
    :param key_id: The Access Key ID for the request sender.

    :type secret_key: string
    :param secret_key: Secret Access Key used for request signature.

    :type parameters: dict
    :param parameters: Optional additional request parameters.

    """
    def __init__(self, endpoint, key_id, secret_key, parameters=None):
        parameters = parameters or dict()
        parsed = urlparse.urlparse(endpoint)
        self.host = parsed.hostname
        self.path = parsed.path or '/'
        self.endpoint = endpoint
        self.secret_key = secret_key
        self.parameters = dict({
            'AWSAccessKeyId': key_id,
            'SignatureVersion': 2,
            'SignatureMethod': 'HmacSHA256',
        }, **parameters)

    @property
    def signed_parameters(self):
        self.parameters['Timestamp'] = datetime.utcnow().isoformat()
        params = dict(self.parameters, **{'Signature': self.signature})
        return urllib.urlencode(params)

    @property
    def signature(self):
        params = urllib.urlencode(sorted(self.parameters.items()))
        text = "\n".join(['POST', self.host, self.path, params])
        auth = hmac.new(str(self.secret_key), msg=text, digestmod=hashlib.sha256)
        return base64.b64encode(auth.digest())


class EucaAuthenticator(object):
    """Eucalyptus cloud token authenticator"""
    TEMPLATE = 'https://{host}:8773/{service}?Action={action}&DurationSeconds={dur}&Version={ver}'

    def __init__(self, host, duration):
        """
        Configure connection to Eucalyptus STS service to authenticate with the CLC (cloud controller)

        :type host: string
        :param host: IP address or FQDN of CLC host

        :type duration: int
        :param duration: Duration of the session token (in seconds)

        """
        self.host = host
        self.duration = duration
        self.auth_url = self.TEMPLATE.format(
            host=self.host,
            dur=duration,
            service='services/Tokens',
            action='GetAccessToken',
            ver='2011-06-15'
        )

    def authenticate(self, account, user, passwd, new_passwd=None, timeout=15):
        duration = self.duration
        if user == 'admin':  # admin cannot have more than 1 hour duration
            duration = 3600
        req = urllib2.Request(self.auth_url)

        if new_passwd:
            auth_string = "{user}@{account};{pw}@{new_pw}".format(
                user=base64.b64encode(user),
                account=base64.b64encode(account),
                pw=base64.b64encode(passwd),
                new_pw=new_passwd
            )
        else:
            auth_string = "{user}@{account}:{pw}".format(
                user=base64.b64encode(user),
                account=base64.b64encode(account),
                pw=passwd
            )
        encoded_auth = base64.b64encode(auth_string)
        req.add_header('Authorization', "Basic %s" % encoded_auth)
        try:
            response = urllib2.urlopen(req, timeout=timeout)
        except Exception:
            auth_url = self.TEMPLATE.format(
                host=self.host,
                dur=duration,
                service='services/Tokens',
                action='GetSessionToken',
                ver='2011-06-15'
            )
            req = urllib2.Request(auth_url)
            req.add_header('Authorization', "Basic %s" % encoded_auth)
            response = urllib2.urlopen(req, timeout=timeout)

        body = response.read()

        # parse AccessKeyId, SecretAccessKey and SessionToken
        creds = Credentials()
        h = BotoXmlHandler(creds, None)
        xml.sax.parseString(body, h)
        logging.info("Authenticated Eucalyptus user: " + account + "/" + user)
        return creds


class AWSAuthenticator(object):

    def __init__(self, package):
        """
        Configure connection to AWS STS service

        :type package: string
        :param package: a pre-signed request string for the STS GetSessionToken call

        """
        self.endpoint = 'https://sts.amazonaws.com'
        self.package = package

    def authenticate(self, timeout=20):
        """ Make authentication request to AWS STS service
            Timeout defaults to 20 seconds"""
        req = urllib2.Request(self.endpoint, data=self.package)
        response = urllib2.urlopen(req, timeout=timeout)
        body = response.read()

        # parse AccessKeyId, SecretAccessKey and SessionToken
        creds = Credentials()
        h = BotoXmlHandler(creds, None)
        xml.sax.parseString(body, h)
        logging.info("Authenticated AWS user")
        return creds

