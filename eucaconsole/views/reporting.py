# -*- coding: utf-8 -*-
# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
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
Pyramid views for Eucalyptus and Usage Reporting

"""
import simplejson as json

from pyramid.view import view_config

from ..i18n import _
from ..views import BaseView, JSONResponse


class ReportingView(BaseView):
    def __init__(self, request):
        super(ReportingView, self).__init__(request)
        self.title_parts = [_(u'Reporting')]

    def is_reporting_configured(self):
        # replace this with logic that checks actual reporting configuration status
        return False

    @view_config(route_name='reporting', renderer='../templates/reporting/reporting.pt')
    def queues_landing(self):
        return dict(
            reporting_configured='true' if self.is_reporting_configured() else 'false'
        )


class ReportingAPIView(BaseView):
    """
    A view for reporting related XHR calls that carrys very little overhead
    """
    def __init__(self, request):
        super(ReportingAPIView, self).__init__(request)
        self.conn = self.get_connection(conn_type='reporting')

    @view_config(route_name='reporting_prefs', renderer='json', request_method='GET', xhr=True)
    def get_reporting_prefs(self):
        # use "ViewBilling" call to fetch billing configuration information
        ret = self.conn.view_billing()
        prefs = ret.get('billingSettings')
        ret = self.conn.view_account()
        acct_prefs = ret.get('accountSettings')
        ret = dict(
            enabled=prefs.get('detailedBillingEnabled'),
            bucketName=prefs.get('reportBucket') or '',
            activeTags=prefs.get('activeCostAllocationTags') or ['one'],
            inactiveTags=prefs.get('inactiveCostAllocationTags') or ['two', 'three', 'four'],
            userReportsEnabled=acct_prefs.get('userBillingAccess'),
        )
        return dict(results=ret)

    @view_config(route_name='reporting_prefs', renderer='json', request_method='PUT', xhr=True)
    def set_reporting_prefs(self):
        params = json.loads(self.request.body)
        csrf_token = params.get('csrf_token')
        if not self.is_csrf_valid(token=csrf_token):
            return JSONResponse(status=400, message="missing CSRF token")
        self.log_request(_(u"Saving report preferences"))
        # use "ModifyBilling" to change billing configuration
        enabled = params.get('enabled')
        bucket_name = params.get('bucketName')
        tags = params.get('tags')
        self.conn.modify_billing(enabled, bucket_name, tags)
        # use "ModifyAccount" to change report access
        user_reports_enabled = params.get('userReportsEnabled')
        self.conn.modify_account(user_reports_enabled)
        return dict(message=_("Successully updated reporting preferences."))

