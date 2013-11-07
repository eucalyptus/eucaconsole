"""
Authentication and Authorization models

"""
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

