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
Forms for Snapshots

"""
import wtforms
from wtforms import validators

from ..i18n import _
from . import BaseSecureForm, NgNonBindableOptionSelect

class SnapshotForm(BaseSecureForm):
    """Snapshot form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    name_error_msg = _(u'Not a valid name')
    name = wtforms.TextField(label=_(u'Name'))
    volume_error_msg = _(u'Volume is required')
    volume_id = wtforms.SelectField(
        label=_(u'Create from volume'),
        validators=[validators.DataRequired(message=volume_error_msg),],
        widget=NgNonBindableOptionSelect(),
    )
    desc_error_msg = _(u'Description is required')
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )

    def __init__(self, request, snapshot=None, conn=None, **kwargs):
        super(SnapshotForm, self).__init__(request, **kwargs)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.snapshot = snapshot
        self.conn = conn
        self.name.error_msg = self.name_error_msg
        self.volume_id.error_msg = self.volume_error_msg
        self.description.error_msg = self.desc_error_msg

        if snapshot is not None:
            self.name.data = snapshot.tags.get('Name', '')
            self.volume_id.data = snapshot.volume_id
            self.description.data = snapshot.description

        if conn is not None:
            self.set_volume_choices()

    def set_volume_choices(self):
        choices = []
        for volume in self.conn.get_all_volumes():
            value = volume.id
            vol_name_tag = volume.tags.get('Name', '')
            label = '{0}{1}'.format(
                volume.id, ' ({0})'.format(vol_name_tag) if vol_name_tag else '')
            choices.append((value, label))
        # Need to insert current choice since the source volume may have been removed after this snapshot was created
        if self.snapshot and self.snapshot.volume_id:
            vol_id = self.snapshot.volume_id
            choices.append((vol_id, vol_id))
        self.volume_id.choices = sorted(choices)


class DeleteSnapshotForm(BaseSecureForm):
    """CSRF-protected form to delete a snapshot"""
    pass


class RegisterSnapshotForm(BaseSecureForm):
    """CSRF-protected form to delete a snapshot"""
    name = wtforms.TextField(label=_(u'Name'),
        validators=[validators.InputRequired(message=_(u'Image name is required'))])
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )
    dot = wtforms.BooleanField(label=_(u'Delete on terminate'))
    reg_as_windows = wtforms.BooleanField(label=_(u'Register as Windows OS image'))


class SnapshotsFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    status = wtforms.SelectMultipleField(label=_(u'Status'))
    tags = wtforms.TextField(label=_(u'Tags'))

    def __init__(self, request, **kwargs):
        super(SnapshotsFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.status.choices = self.get_status_choices()

    @staticmethod
    def get_status_choices():
        return (
            ('pending', 'In progress'),
            ('completed', 'Completed'),
        )

