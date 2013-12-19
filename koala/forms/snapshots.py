"""
Forms for Snapshots

"""
import wtforms
from wtforms import validators

from pyramid.i18n import TranslationString as _

from . import BaseSecureForm


class SnapshotForm(BaseSecureForm):
    """Snapshot form
       Note: no need to add a 'tags' field.  Use the tag_editor panel (in a template) instead
    """
    name = wtforms.TextField(label=_(u'Name'))
    volume_error_msg = _(u'Volume is required')
    volume_id = wtforms.SelectField(
        label=_(u'Create from volume'),
        validators=[validators.Required(message=volume_error_msg),]
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
        self.volume_id.error_msg = self.volume_error_msg
        self.description.error_msg = self.desc_error_msg

        if snapshot is not None:
            self.name.data = snapshot.tags.get('Name', '')
            self.volume_id.data = snapshot.volume_id
            self.description.data = snapshot.description

        if conn is not None:
            self.set_volume_choices()

    def set_volume_choices(self):
        choices = [('', _(u'select...'))]
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
        validators=[validators.Required(message=_(u'Image name is required'))])
    description = wtforms.TextAreaField(
        label=_(u'Description'),
        validators=[
            validators.Length(max=255, message=_(u'Description must be less than 255 characters'))
        ],
    )
    dot = wtforms.BooleanField(label=_(u'Delete on terminate'))
    reg_as_windows = wtforms.BooleanField(label=_(u'Register as Windows OS image'))

