# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS snapshots

"""
from dateutil import parser
import simplejson as json

from boto.exception import BotoServerError
from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.snapshots import SnapshotForm, DeleteSnapshotForm, RegisterSnapshotForm, SnapshotsFiltersForm
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, BaseView
from ..views.images import ImagesView
from . import boto_error_handler


class SnapshotsView(LandingPageView):
    VIEW_TEMPLATE = '../templates/snapshots/snapshots.pt'

    def __init__(self, request):
        super(SnapshotsView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.initial_sort_key = '-start_time'
        self.prefix = '/snapshots'
        self.json_items_endpoint = self.get_json_endpoint('snapshots_json')
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.register_form = RegisterSnapshotForm(self.request, formdata=self.request.params or None)
        self.filters_form = SnapshotsFiltersForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            prefix=self.prefix,
            delete_form=self.delete_form,
            register_form=self.register_form,
            filters_form=self.filters_form,
        )

    @view_config(route_name='snapshots', renderer=VIEW_TEMPLATE)
    def snapshots_landing(self):
        filter_keys = ['id', 'name', 'volume_size', 'start_time', 'tags', 'volume_id', 'status']
        self.render_dict.update(dict(
            filter_keys=filter_keys,
            filter_fields=True,
            sort_keys=self.get_sort_keys(),
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
        ))
        return self.render_dict

    @view_config(route_name='snapshots_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshots_delete(self):
        snapshot_id = self.request.params.get('snapshot_id')
        volume_id = self.request.params.get('volume_id')
        snapshot = self.get_snapshot(snapshot_id)
        location = self.get_redirect_location('snapshots')
        if volume_id:
            location = self.request.route_path('volume_snapshots', id=volume_id)
        if snapshot and self.delete_form.validate():
            with boto_error_handler(self.request, location):
                BaseView.log_request(self.request, _(u"Deleting snapshot {0}").format(snapshot_id))
                snapshot.delete()
                prefix = _(u'Successfully deleted snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to delete snapshot')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    @view_config(route_name='snapshots_register', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshots_register(self):
        snapshot_id = self.request.params.get('snapshot_id')
        snapshot = self.get_snapshot(snapshot_id) if snapshot_id != 'new' else None
        name = self.request.params.get('name')
        description = self.request.params.get('description')
        dot = self.request.params.get('dot')
        reg_as_windows = self.request.params.get('reg_as_windows')
        root_vol = BlockDeviceType(snapshot_id=snapshot_id)
        root_vol.delete_on_termination = dot
        bdm = BlockDeviceMapping()
        # ok to keep this sda since we're setting new value
        bdm['/dev/sda'] = root_vol
        location = self.get_redirect_location('snapshots')
        if snapshot and self.register_form.validate():
            with boto_error_handler(self.request, location):
                image_id = snapshot.connection.register_image(
                    name=name,
                    description=description,
                    kernel_id=('windows' if reg_as_windows else None),
                    block_device_map=bdm
                )
                prefix = _(u'Successfully registered snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                # Clear images cache
                ImagesView.clear_images_cache()
                location = self.request.route_path('image_view', id=image_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to register snapshot')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    def get_snapshot(self, snapshot_id):
        if snapshot_id:
            snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
            return snapshots_list[0] if snapshots_list else None
        return None

    @staticmethod
    def get_sort_keys():
        """sort_keys are passed to sorting drop-down on landing page"""
        return [
            dict(key='start_time', name=_(u'Start time: Oldest to Newest')),
            dict(key='-start_time', name=_(u'Start time: Newest to Oldest')),
            dict(key='volume_size', name=_(u'Size')),
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='status', name=_(u'Status')),
            dict(key='volume_id', name=_(u'Volume ID')),
        ]


class SnapshotsJsonView(LandingPageView):
    def __init__(self, request):
        super(SnapshotsJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='snapshots_json', renderer='json', request_method='GET')
    def snapshots_json(self):
        snapshots = []
        filtered_snapshots = self.filter_items(self.get_items())
        volume_ids = list(set([snapshot.volume_id for snapshot in filtered_snapshots]))
        volumes = self.conn.get_all_volumes(volume_ids=volume_ids) if self.conn else []
        for snapshot in filtered_snapshots:
            volume = [volume for volume in volumes if volume.id == snapshot.volume_id]
            volume_name = ''
            if volume:
                volume_name = TaggedItemView.get_display_name(volume[0])
            snapshots.append(dict(
                id=snapshot.id,
                description=snapshot.description,
                name=snapshot.tags.get('Name', snapshot.id),
                progress=snapshot.progress,
                transitional=self.is_transitional(snapshot),
                start_time=snapshot.start_time,
                status=snapshot.status,
                tags=TaggedItemView.get_tags_display(snapshot.tags, wrap_width=36),
                volume_id=snapshot.volume_id,
                volume_name=volume_name,
                volume_size=snapshot.volume_size,
            ))
        return dict(results=snapshots)

    def get_items(self):
        return self.conn.get_all_snapshots(owner='self') if self.conn else []

    @staticmethod
    def is_transitional(snapshot):
        if snapshot.status.lower() == 'completed':
            return False
        return int(snapshot.progress.replace('%', '')) < 100


class SnapshotView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/snapshots/snapshot_view.pt'

    def __init__(self, request):
        super(SnapshotView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.location = self.request.route_path('snapshot_view', id=self.request.matchdict.get('id'))
        with boto_error_handler(request, self.location):
            self.snapshot = self.get_snapshot()
        self.snapshot_name = self.get_snapshot_name()
        self.volume_name = TaggedItemView.get_display_name(
            self.get_volume(self.snapshot.volume_id)) if self.snapshot is not None else ''
        if self.volume_name == '':
            self.volume_name = self.snapshot.volume_id if self.snapshot else ''
        self.snapshot_form = SnapshotForm(
            self.request, snapshot=self.snapshot, conn=self.conn, formdata=self.request.params or None)
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.register_form = RegisterSnapshotForm(self.request, formdata=self.request.params or None)
        self.start_time = self.get_start_time()
        self.tagged_obj = self.snapshot
        with boto_error_handler(request, self.location):
            self.images_registered = self.get_images_registered(self.snapshot.id) if self.snapshot else None
        self.render_dict = dict(
            snapshot=self.snapshot,
            registered=True if self.images_registered is not None else False,
            snapshot_name=self.snapshot_name,
            snapshot_start_time=self.start_time,
            volume_name=self.volume_name,
            snapshot_form=self.snapshot_form,
            delete_form=self.delete_form,
            register_form=self.register_form,
        )

    def get_root_device_name(self, img):
        return img.root_device_name.replace('&#x2f;', '/').replace(
            '&#x2f;', '/') if img.root_device_name is not None else '/dev/sda'

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

    def get_start_time(self):
        """Returns instance launch time as a python datetime.datetime object"""
        if self.snapshot and self.snapshot.start_time:
            return parser.parse(self.snapshot.start_time)
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
            location = self.request.route_path('snapshot_view', id=self.snapshot.id)
            with boto_error_handler(self.request, location):
                self.update_tags()
                msg = _(u'Successfully modified snapshot')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.snapshot_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='snapshot_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshot_create(self):
        if self.snapshot_form.validate():
            name = self.request.params.get('name', '')
            description = self.request.params.get('description', '')
            tags_json = self.request.params.get('tags')
            volume_id = self.request.params.get('volume_id')
            with boto_error_handler(self.request, self.request.route_path('snapshot_create')):
                BaseView.log_request(self.request, _(u"Creating snapshot from volume {0}").format(volume.id))
                snapshot = self.conn.create_snapshot(volume_id, description=description)
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
                location = self.request.route_path('snapshot_view', id=snapshot.id)
                return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='snapshot_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshot_delete(self):
        if self.snapshot and self.delete_form.validate():
            with boto_error_handler(self.request, self.request.route_path('snapshots')):
                BaseView.log_request(self.request, _(u"Deleting snapshot {0}").format(self.snapshot.id))
                if self.images_registered is not None:
                    for img in self.images_registered:
                        img.deregister()
                    # Clear images cache
                    ImagesView.clear_images_cache()
                self.snapshot.delete()
                prefix = _(u'Successfully deleted snapshot.')
                msg = '{prefix} {id}'.format(prefix=prefix, id=self.snapshot.id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            location = self.request.route_path('snapshots')
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
        location = self.request.route_path('snapshot_view', id=snapshot_id)
        if self.snapshot and self.register_form.validate():
            with boto_error_handler(self.request, location):
                BaseView.log_request(self.request, _(u"Registering snapshot {0} as image {1}").format(snapshot_id, name))
                self.snapshot.connection.register_image(
                    name=name, description=description,
                    kernel_id=('windows' if reg_as_windows else None),
                    block_device_map=bdm)
                prefix = _(u'Successfully registered snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                # Clear images cache
                ImagesView.clear_images_cache()
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    def get_snapshot(self):
        snapshot_id = self.request.matchdict.get('id')
        if snapshot_id:
            if snapshot_id == 'new':
                return None
            snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
            return snapshots_list[0] if snapshots_list else None
        return None

    def get_volume(self, volume_id):
        volumes_list = []
        try:
            volumes_list = self.conn.get_all_volumes(volume_ids=[volume_id])
        except BotoServerError as err:
            return None
        return volumes_list[0] if volumes_list else None


class SnapshotStateView(BaseView):
    def __init__(self, request):
        super(SnapshotStateView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        with boto_error_handler(request):
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
