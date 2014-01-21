# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS snapshots

"""
import simplejson as json
import time

from boto.exception import EC2ResponseError
from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.snapshots import SnapshotForm, DeleteSnapshotForm, RegisterSnapshotForm
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, BaseView


class SnapshotsView(LandingPageView):
    VIEW_TEMPLATE = '../templates/snapshots/snapshots.pt'

    def __init__(self, request):
        super(SnapshotsView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.initial_sort_key = '-start_time'
        self.prefix = '/snapshots'
        self.json_items_endpoint = self.request.route_url('snapshots_json')
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.register_form = RegisterSnapshotForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            display_type=self.display_type,
            prefix=self.prefix,
            delete_form=self.delete_form,
            register_form=self.register_form,
        )

    @view_config(route_name='snapshots', renderer=VIEW_TEMPLATE)
    def snapshots_landing(self):
        filter_keys = ['id', 'name', 'volume_size', 'start_time', 'tags', 'volume_id', 'status']
        self.render_dict.update(dict(
            filter_keys=filter_keys,
            filter_fields=self.filter_fields,
            sort_keys=self.get_sort_keys(),
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
        ))
        return self.render_dict

    @view_config(route_name='snapshots_json', renderer='json', request_method='GET')
    def snapshots_json(self):
        snapshots = []
        for snapshot in self.get_items():
            volume = self.get_volume(snapshot.volume_id)
            volume_name = TaggedItemView.get_display_name(volume)
            snapshots.append(dict(
                id=snapshot.id,
                description=snapshot.description,
                name=snapshot.tags.get('Name', snapshot.id),
                progress=snapshot.progress,
                start_time=snapshot.start_time,
                status=snapshot.status,
                tags=TaggedItemView.get_tags_display(snapshot.tags, wrap_width=36),
                volume_id=snapshot.volume_id,
                volume_name=volume_name,
                volume_size=snapshot.volume_size,
            ))
        return dict(results=snapshots)

    @view_config(route_name='snapshots_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshots_delete(self):
        snapshot_id = self.request.params.get('snapshot_id')
        snapshot = self.get_snapshot(snapshot_id)
        display_type = self.request.params.get('display', self.display_type)
        location = '{0}?display={1}'.format(self.request.route_url('snapshots'), display_type)
        if snapshot and self.delete_form.validate():
            try:
                snapshot.delete()
                time.sleep(1)
                prefix = _(u'Successfully deleted snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to delete snapshot')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    @view_config(route_name='snapshots_register', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshots_register(self):
        snapshot_id = self.request.params.get('snapshot_id')
        snapshot = self.get_snapshot(snapshot_id)
        name = self.request.params.get('name')
        description = self.request.params.get('description')
        dot = self.request.params.get('dot')
        reg_as_windows = self.request.params.get('reg_as_windows')
        root_vol = BlockDeviceType(snapshot_id=snapshot_id)
        root_vol.delete_on_termination = dot
        bdm = BlockDeviceMapping()
        bdm['/dev/sda'] = root_vol
        display_type = self.request.params.get('display', self.display_type)
        location = '{0}?display={1}'.format(self.request.route_url('snapshots'), display_type)
        if snapshot and self.register_form.validate():
            try:
                snapshot.connection.register_image(name=name, description=description,
                        kernel_id=('windows' if reg_as_windows else None),
                        block_device_map=bdm)
                time.sleep(1)
                prefix = _(u'Successfully registered snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to register snapshot')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    def get_items(self):
        # TODO: cache me
        return self.conn.get_all_snapshots(owner='self') if self.conn else []

    def get_snapshot(self, snapshot_id):
        if snapshot_id:
            snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
            return snapshots_list[0] if snapshots_list else None
        return None

    def get_volume(self, volume_id):
        if volume_id:
            volumes_list = self.conn.get_all_volumes(volume_ids=[volume_id])
            return volumes_list[0] if volumes_list else None
        return None

    @staticmethod
    def get_sort_keys():
        """sort_keys are passed to sorting drop-down on landing page"""
        return [
            dict(key='-start_time', name=_(u'Start time')),
            dict(key='volume_size', name=_(u'Size')),
            dict(key='name', name=_(u'Name')),
            dict(key='status', name=_(u'Status')),
            dict(key='volume_id', name=_(u'Volume ID')),
        ]


class SnapshotView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/snapshots/snapshot_view.pt'

    def __init__(self, request):
        super(SnapshotView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.snapshot = self.get_snapshot()
        self.snapshot_name = self.get_snapshot_name()
        self.volume_name = TaggedItemView.get_display_name(self.get_volume(self.snapshot.volume_id)) if self.snapshot is not None else ''
        self.snapshot_form = SnapshotForm(
            self.request, snapshot=self.snapshot, conn=self.conn, formdata=self.request.params or None)
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.register_form = RegisterSnapshotForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.snapshot
        self.images_registered = self.get_images_registered(self.snapshot.id) if self.snapshot else None
        self.render_dict = dict(
            snapshot=self.snapshot,
            registered=True if self.images_registered is not None else False,
            snapshot_name=self.snapshot_name,
            volume_name=self.volume_name,
            snapshot_form=self.snapshot_form,
            delete_form=self.delete_form,
            register_form=self.register_form,
        )

    def get_root_device_name(self, img):
        return img.root_device_name.replace('&#x2f;', '/').replace(
            '&#x2f;', '/') if img.root_device_name is not None else '/dev/sda1'

    def get_images_registered(self, snap_id):
        ret = []
        images = self.conn.get_all_images(owners='self')
        for img in images:
            if img.block_device_mapping is not None:
                vol = img.block_device_mapping[self.get_root_device_name(img)]
                if vol is not None and snap_id == vol.snapshot_id:
                    ret.append(img)
        return ret or None

    def get_snapshot_name(self):
        if self.snapshot:
            return TaggedItemView.get_display_name(self.snapshot)
        return None

    @view_config(route_name='snapshot_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def snapshot_view(self):
        if self.snapshot is None and self.request.matchdict.get('id') != 'new':
            raise HTTPNotFound
        return self.render_dict

    @view_config(route_name='snapshot_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshot_update(self):
        if self.snapshot and self.snapshot_form.validate():
            # Update tags
            self.update_tags()

            location = self.request.route_url('snapshot_view', id=self.snapshot.id)
            msg = _(u'Successfully modified snapshot')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='snapshot_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshot_create(self):
        if self.snapshot_form.validate():
            name = self.request.params.get('name', '')
            description = self.request.params.get('description', '')
            tags_json = self.request.params.get('tags')
            volume_id = self.request.params.get('volume_id')
            try:
                volume = self.get_volume(volume_id)
                snapshot = volume.create_snapshot(description)
                # Add name tag
                if name:
                    snapshot.add_tag('Name', name)
                if tags_json:
                    tags = json.loads(tags_json)
                    for tagname, tagvalue in tags.items():
                        snapshot.add_tag(tagname, tagvalue)
                msg = _(u'Successfully sent create snapshot request.  It may take a moment to create the snapshot.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
                location = self.request.route_url('snapshot_view', id=snapshot.id)
                return HTTPFound(location=location)
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
                self.request.session.flash(msg, queue=queue)
        return self.render_dict

    @view_config(route_name='snapshot_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshot_delete(self):
        if self.snapshot and self.delete_form.validate():
            try:
                if self.images_registered is not None:
                    for img in self.images_registered:
                        img.deregister()
                self.snapshot.delete()
                time.sleep(1)
                prefix = _(u'Successfully deleted snapshot.')
                msg = '{prefix} {id}'.format(prefix=prefix, id=self.snapshot.id)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            location = self.request.route_url('snapshots')
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='snapshot_register', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshot_register(self):
        snapshot_id = self.snapshot.id
        name = self.request.params.get('name')
        description = self.request.params.get('description')
        dot = self.request.params.get('dot')
        reg_as_windows = self.request.params.get('reg_as_windows')
        root_vol = BlockDeviceType(snapshot_id=snapshot_id)
        root_vol.delete_on_termination = dot
        bdm = BlockDeviceMapping()
        bdm['/dev/sda'] = root_vol
        if self.snapshot and self.register_form.validate():
            try:
                self.snapshot.connection.register_image(name=name, description=description,
                        kernel_id=('windows' if reg_as_windows else None),
                        block_device_map=bdm)
                time.sleep(1)
                prefix = _(u'Successfully registered snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            location = self.request.route_url('snapshots')
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def get_snapshot(self):
        snapshot_id = self.request.matchdict.get('id')
        if snapshot_id:
            snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
            return snapshots_list[0] if snapshots_list else None
        return None

    def get_volume(self, volume_id):
        volumes_list = self.conn.get_all_volumes(volume_ids=[volume_id])
        return volumes_list[0] if volumes_list else None


class SnapshotStateView(BaseView):
    def __init__(self, request):
        super(SnapshotStateView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.snapshot = self.get_snapshot()

    @view_config(route_name='snapshot_size_json', renderer='json', request_method='GET')
    def snapshot_size_json(self):
        """Return current snapshot size"""
        return dict(results=self.snapshot.volume_size)

    @view_config(route_name='snapshot_state_json', renderer='json', request_method='GET')
    def snapshot_state_json(self):
        """Return current snapshot state"""
        status = self.snapshot.status
        progress = self.snapshot.progress
        return dict(
            results=dict(status=status, progress=progress)
        )

    def get_snapshot(self):
        snapshot_id = self.request.matchdict.get('id')
        if snapshot_id:
            snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
            return snapshots_list[0] if snapshots_list else None
        return None

