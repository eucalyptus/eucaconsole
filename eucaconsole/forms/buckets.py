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
Forms for S3 buckets and objects

"""
import wtforms
from wtforms import validators

from . import BaseSecureForm
from ..i18n import _


class BucketDetailsForm(BaseSecureForm):
    """S3 BucketDetails form"""
    pass


class SharingPanelForm(BaseSecureForm):
    """S3 Sharing Panel form for buckets/objects"""
    SHARE_TYPE_CHOICES = (('public', _(u'Public')), ('private', _(u'Private')))
    share_type = wtforms.RadioField(choices=SHARE_TYPE_CHOICES)
    share_account = wtforms.SelectField(label=_(u'Account'))
    share_permissions = wtforms.SelectField(label=_(u'Permissions'))

    def __init__(self, request, bucket_object=None, sharing_acl=None, **kwargs):
        super(SharingPanelForm, self).__init__(request, **kwargs)
        self.bucket_object = bucket_object
        self.sharing_acl = sharing_acl
        # Set choices
        self.share_account.choices = self.get_account_choices()
        self.share_permissions.choices = self.get_permission_choices()

        if bucket_object is not None:
            self.share_type.data = self.get_share_type()

    def get_share_type(self):
        if 'AllUsers = READ' in str(self.sharing_acl):
            return 'public'
        return 'private'

    @staticmethod
    def get_permission_choices():
        return (
            ('READ', _('Read-only')),
            ('WRITE', _('Read-Write')),
            ('READ_ACP', _('Read sharing permissions')),
            ('WRITE_ACP', _('Write sharing permissions')),
        )

    @staticmethod
    def get_account_choices():
        # TODO: replace with accounts API fetch
        return (
            ('', _(u'Select...')),
            ('joeuser|||17c108447e01c1d9c126bcd52c38dbeb9e54555eeb350d1c9e4dfa6b627afab6', 'joeuser'),
        )


