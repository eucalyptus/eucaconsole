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
Forms for Elastic IP operations

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, ChoicesManager


class AllocateIPsForm(BaseSecureForm):
    """Allocate IP Addresses form, used on IP Addresses landing page in modal dialog"""
    domain = wtforms.SelectField(label=_(u'Scope'))
    ipcount_error_msg = _(u'Please enter a whole number greater than zero')
    ipcount = wtforms.IntegerField(
        label=_(u'Number of addresses'),
        validators=[validators.InputRequired(message=ipcount_error_msg)],
    )

    def __init__(self, request, **kwargs):
        super(AllocateIPsForm, self).__init__(request, **kwargs)
        self.domain.choices = [(_(u'standard'), _(u'Standard')), (_(u'vpc'), _(u'VPC'))]
        self.ipcount.data = 1
        self.ipcount.error_msg = self.ipcount_error_msg


class AssociateIPForm(BaseSecureForm):
    """Associate an Elastic IP with an instance"""
    instance_error_msg = _(u'Instance is required')
    instance_id = wtforms.SelectField(
        label=_(u'Instance:'),
        validators=[validators.InputRequired(message=instance_error_msg)],
    )

    def __init__(self, request, conn=None, **kwargs):
        super(AssociateIPForm, self).__init__(request, **kwargs)
        self.conn = conn
        self.choices_manager = ChoicesManager(conn=self.conn)
        self.instance_id.choices = self.choices_manager.instances(state="running")
        self.instance_id.error_msg = self.instance_error_msg


class DisassociateIPForm(BaseSecureForm):
    """No fields required here except the CSRF token"""
    pass


class ReleaseIPForm(BaseSecureForm):
    """No fields required here except the CSRF token"""
    pass


class IPAddressesFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    assignment = wtforms.SelectMultipleField(label=_(u'Assignment'))

    def __init__(self, request, conn=None, **kwargs):
        super(IPAddressesFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.assignment.choices = self.get_assignment_choices()

    @staticmethod
    def get_assignment_choices():
        return (
            ('assigned', 'Assigned'),
            ('', 'Unassigned'),
        )

