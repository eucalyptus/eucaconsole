"""
Authentication and Authorization models

"""
import base64
import logging
import urllib2
import xml

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
    return [Authenticated]


class TokenAuthenticator(object):
    def __init__(self, host, duration):
        # make the call to STS service to authenticate with the CLC
        self.auth_url = "https://{host}:8773/{service}?Action={action}&DurationSeconds={dur}&Version={ver}".format(
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
        logging.info("authenticated user: " + account + "/" + user)
        return creds

    # raises EuiExcepiton for "Not Authorized" or "Timed out"
    def authenticate_aws(self, package):
        req = urllib2.Request('https://sts.amazonaws.com', package)
        response = urllib2.urlopen(req, timeout=20)
        body = response.read()

        # parse AccessKeyId, SecretAccessKey and SessionToken
        creds = Credentials(None)
        h = BotoXmlHandler(creds, None)
        xml.sax.parseString(body, h)
        logging.info("authenticated aws user")
        return creds
