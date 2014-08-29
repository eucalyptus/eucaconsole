# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
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
        landingpage_route_paths = [self.request.route_url(name) for name in LANDINGPAGE_ROUTE_NAMES]
        if return_to_path not in landingpage_route_paths:
            return_to = self.request.route_path('dashboard')
        region = self.request.params.get('region')
        # NOTE: We normally don't want a GET request to modify data,
        #       but we're only updating the selected region in the session here.
        self.request.session['region'] = region
        return HTTPFound(location=return_to)

