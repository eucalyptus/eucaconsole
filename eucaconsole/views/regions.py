# -*- coding: utf-8 -*-
"""
Region selector view

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from . import BaseView
from ..constants import LANDINGPAGE_ROUTE_NAMES


class RegionSelectView(BaseView):
    """Region selector"""

    @view_config(route_name='region_select', request_method='GET')
    def select_region(self):
        """Select region and redirect to referring page"""
        return_to = self.request.params.get('returnto')
        return_to_path = return_to
        landingpage_route_paths = [self.request.route_path(name) for name in LANDINGPAGE_ROUTE_NAMES]
        if return_to_path not in landingpage_route_paths:
            return_to = self.request.route_path('dashboard')
        region = self.request.params.get('region')
        # NOTE: We normally don't want a GET request to modify data,
        #       but we're only updating the selected region in the session here.
        self.request.session['region'] = region
        return HTTPFound(location=return_to)

