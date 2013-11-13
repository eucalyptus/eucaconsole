"""
Region selector view

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from . import BaseView


class RegionSelectView(BaseView):
    """Region selector"""

    @view_config(route_name='region_select', request_method='GET')
    def select_region(self):
        """Select region and redirect to referring page"""
        return_to = self.request.params.get('returnto')
        region = self.request.params.get('region')
        # NOTE: We normally don't want a GET request to modify data,
        #       but we're only updating the selected region in the session here.
        self.request.session['region'] = region
        return HTTPFound(location=return_to)

