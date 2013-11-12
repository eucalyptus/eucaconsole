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

from boto.handler import XmlHandler as BotoXmlHandler
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

    def __init__(self, host, duration):
        """
        Configure connection to Eucalyptus STS service to authenticate with the CLC (cloud controller)

        :type host: string
        :param host: IP address or FQDN of CLC host

        :type duration: int
        :param duration: Duration of the session token (in seconds)

        """
        template = 'https://{host}:8773/{service}?Action={action}&DurationSeconds={dur}&Version={ver}'
        self.auth_url = template.format(
            host=host,
            dur=duration,
            service='services/Tokens',
            action='GetSessionToken',
            ver='2011-06-15'
        )

    def authenticate(self, account, user, passwd, new_passwd=None, timeout=15):
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
        response = urllib2.urlopen(req, timeout=timeout)
        body = response.read()

        # parse AccessKeyId, SecretAccessKey and SessionToken
        creds = Credentials(None)
        h = BotoXmlHandler(creds, None)
        xml.sax.parseString(body, h)
        logging.info("Authenticated Eucalyptus user: " + account + "/" + user)
        return creds


class AWSAuthenticator(AWSQuery):

    def __init__(self, key_id, secret_key, duration):
        """
        Configure connection to AWS STS service

        :type key_id: string
        :param key_id: AWS access key

        :type secret_key: string
        :param secret_key: AWS secret key

        :type duration: int
        :param duration: Duration of AWS session token, in seconds

        """
        self.endpoint = 'https://sts.amazonaws.com'
        params = dict(
            Action='GetSessionToken',
            DurationSeconds=duration,
            Version='2011-06-15'
        )
        super(AWSAuthenticator, self).__init__(self.endpoint, key_id, secret_key, parameters=params)

    def authenticate(self, timeout=20):
        """ Make authentication request to AWS STS service
            Timeout defaults to 20 seconds"""
        req = urllib2.Request(self.endpoint, data=self.signed_parameters)
        response = urllib2.urlopen(req, timeout=timeout)
        body = response.read()

        # parse AccessKeyId, SecretAccessKey and SessionToken
        creds = Credentials(None)
        h = BotoXmlHandler(creds, None)
        xml.sax.parseString(body, h)
        logging.info("Authenticated AWS user")
        return creds

