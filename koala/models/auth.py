"""
Authentication and Authorization models

"""
from pyramid.security import Authenticated


def groupfinder(user_id, request):
    return [Authenticated]

