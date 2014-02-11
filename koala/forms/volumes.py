# -*- coding: utf-8 -*-
"""
Forms for Volumes

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm, ChoicesManager


class VolumeForm(BaseSecureForm):
    """Volume form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    name = wtforms.TextField(label=_(u'Name'))
    snapshot_id = wtforms.SelectField(label=_(u'Create from snapshot?'))
    size_error_msg = _(u'Volume size is required')
    size = wtforms.TextField(
        label=_(u'Volume size (GB)'),
        validators=[validators.DataRequired(message=size_error_msg)],
    )
    zone_error_msg = _(u'Availability zone is required')
    zone = wtforms.SelectField(
        label=_(u'Availability zone'),
        validators=[validators.DataRequired(message=zone_error_msg)],
    )

    def __init__(self, request, conn=None, volume=None, snapshots=None, zones=None, **kwargs):
        """
        :param snapshots: list of snapshot objects
        :param zones: list of availability zones

        """
        super(VolumeForm, self).__init__(request, **kwargs)
        self.cloud_type = request.session.get('cloud_type', 'euca')
        self.conn = conn
        self.volume = volume
        self.snapshots = snapshots or []
        self.zones = zones or []
        self.size.error_msg = self.size_error_msg
        self.zone.error_msg = self.zone_error_msg
        self.choices_manager = ChoicesManager(conn=conn)
        self.set_choices()

        if volume is not None:
            self.name.data = volume.tags.get('Name', '')
            self.size.data = volume.size
            self.snapshot_id.data = volume.snapshot_id if volume.snapshot_id else ''
            self.zone.data = volume.zone

    def set_choices(self):
        self.set_volume_snapshot_choices()
        self.zone.choices = self.choices_manager.availability_zones(zones=self.zones, add_blank=False)

        # default to first zone if new volume, and at least one zone in list
        if self.volume is None and len(self.zones) > 0:
            self.zone.data = self.zones[0].name

    def set_volume_snapshot_choices(self):
        choices = [('', _(u'None'))]
        # TODO: May need to filter get_all_snapshots() call for AWS?
        for snapshot in self.snapshots:
            value = snapshot.id
            name = snapshot.tags.get('Name', None)
            if name is not None:
                label = '{name} ({id})'.format(name=name, id=value)
            else:
                label = str(value)
            choices.append((value, label))
        # Need to insert current choice since the source snapshot may have been removed after this volume was created
        if self.volume and self.volume.snapshot_id:
            snap_id = self.volume.snapshot_id
            choices.append((snap_id, snap_id))
        self.snapshot_id.choices = sorted(choices)


class DeleteVolumeForm(BaseSecureForm):
    """CSRF-protected form to delete a volume"""
    pass


class CreateSnapshotForm(BaseSecureForm):
    """CSRF-protected form to create a snapshot from a volume"""
    name = wtforms.TextField(label=_(u'Name'))
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )

    def __init__(self, request, **kwargs):
        super(CreateSnapshotForm, self).__init__(request, **kwargs)
        self.request = request


class DeleteSnapshotForm(BaseSecureForm):
    """CSRF-protected form to delete a snapshot from a volume"""
    pass


class AttachForm(BaseSecureForm):
    """CSRF-protected form to attach a volume to a selected instance
       Note: This is for attaching a volume to a choice of instances on the volume detail page
             The form to attach a volume to an instance at the instance page is at forms.instances.AttachVolumeForm
    """
    instance_error_msg = _(u'Instance is required')
    instance_id = wtforms.SelectField(
        label=_(u'Instance'),
        validators=[validators.InputRequired(message=instance_error_msg)],
    )
    device_error_msg = _(u'Device is required')
    device = wtforms.TextField(
        label=_(u'Device'),
        validators=[validators.InputRequired(message=device_error_msg)],
    )

    # requires instances which comes from: self.conn.get_only_instances()
    def __init__(self, request, volume=None, instances=None, **kwargs):
        super(AttachForm, self).__init__(request, **kwargs)
        self.request = request
        self.volume = volume
        self.instances = instances or []
        self.instance_id.error_msg = self.instance_error_msg
        self.device.error_msg = self.device_error_msg
        self.set_instance_choices()

    def set_instance_choices(self):
        """Populate instance field with instances available to attach volume to"""
        if self.volume:
            choices = [('', _(u'select...'))]
            for instance in self.instances:
                if self.volume.zone == instance.placement:
                    name_tag = instance.tags.get('Name')
                    extra = ' ({name})'.format(name=name_tag) if name_tag else ''
                    vol_name = '{id}{extra}'.format(id=instance.id, extra=extra)
                    choices.append((instance.id, vol_name))
            if len(choices) == 1:
                choices = [('', _(u'No available instances in the same availability zone'))]
            self.instance_id.choices = choices
        else:
            # We need to set all instances as choices for the landing page to avoid failed validation of instance field
            # The landing page JS restricts the choices based on the selected volume's availability zone
            self.instance_id.choices = [(instance.id, instance.id) for instance in self.instances]


class DetachForm(BaseSecureForm):
    """CSRF-protected form to detach a volume from an instance"""
    pass


class VolumesFiltersForm(BaseSecureForm):
    """Form class for filters on landing page"""
    zone = wtforms.SelectMultipleField(label=_(u'Availability zones'))
    status = wtforms.SelectMultipleField(label=_(u'Status'))
    tags = wtforms.TextField(label=_(u'Tags'))

    def __init__(self, request, conn=None, **kwargs):
        super(VolumesFiltersForm, self).__init__(request, **kwargs)
        self.request = request
        self.choices_manager = ChoicesManager(conn=conn)
        self.zone.choices = self.get_availability_zone_choices()
        self.status.choices = self.get_status_choices()

    def get_availability_zone_choices(self):
        return self.choices_manager.availability_zones(add_blank=False)

    @staticmethod
    def get_status_choices():
        return (
            ('available', 'Available'),
            ('in-use', 'In use'),
        )
