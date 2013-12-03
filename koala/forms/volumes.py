# -*- coding: utf-8 -*-
"""
Forms for Volumes

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class VolumeForm(BaseSecureForm):
    """Volume form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    name = wtforms.TextField(label=_(u'Name'))
    snapshot_id = wtforms.SelectField(label=_(u'Create from snapshot?'))
    size_error_msg = _(u'Volume size is required')
    size = wtforms.TextField(
        label=_(u'Volume size (GB)'),
        validators=[validators.Required(message=size_error_msg)],
    )
    zone_error_msg = _(u'Availability zone is required')
    zone = wtforms.SelectField(
        label=_(u'Availability zone'),
        validators=[validators.Required(message=zone_error_msg)],
    )

    def __init__(self, request, volume=None, conn=None, **kwargs):
        super(VolumeForm, self).__init__(request, **kwargs)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.volume = volume
        self.conn = conn
        self.size.error_msg = self.size_error_msg
        self.zone.error_msg = self.zone_error_msg

        if volume is not None:
            self.name.data = volume.tags.get('Name', '')
            self.size.data = volume.size
            self.snapshot_id.data = volume.snapshot_id if volume.snapshot_id else ''
            self.zone.data = volume.zone

        if conn is not None:
            self.set_volume_snapshot_choices()
            self.set_availability_zone_choices()

    def set_volume_snapshot_choices(self):
        choices = [('', _(u'None'))]
        # TODO: May need to filter get_all_snapshots() call for AWS?
        for snapshot in self.conn.get_all_snapshots():
            choices.append((snapshot.id, snapshot.id))
        self.snapshot_id.choices = sorted(choices)

    def set_availability_zone_choices(self):
        choices = [('', _(u'select...'))]
        for zone in self.conn.get_all_zones():
            choices.append((zone.name, zone.name))
        self.zone.choices = sorted(choices)


class DeleteVolumeForm(BaseSecureForm):
    """CSRF-protected form to delete a volume"""
    pass

