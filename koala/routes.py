"""
URL dispatch routes

"""
from collections import namedtuple


# Simple container to hold a route
Route = namedtuple('Route', ['name', 'pattern'])

urls = [
    Route(name='home', pattern='/'),
    Route(name='instances', pattern='/instances'),
    Route(name='instances_json', pattern='/instances/json'),
]
