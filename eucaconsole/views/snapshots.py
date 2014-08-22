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
Pyramid views for Eucalyptus and AWS snapshots

"""
import simplejson as json

from boto.exception import BotoServerError
from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..forms.snapshots import SnapshotForm, DeleteSnapshotForm, RegisterSnapshotForm, SnapshotsFiltersForm
from ..i18n import _
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, BaseView, JSONResponse
from . import boto_error_handler


class SnapshotsView(LandingPageView):
    VIEW_TEMPLATE = '../templates/snapshots/snapshots.pt'

    def __init__(self, request):
        super(SnapshotsView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.prefix = '/snapshots'
        self.initial_sort_key = '-start_time'
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.register_form = RegisterSnapshotForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            prefix=self.prefix,
            delete_form=self.delete_form,
            register_form=self.register_form,
        )

    @view_config(route_name='snapshots', renderer=VIEW_TEMPLATE)
    def snapshots_landing(self):
        filter_keys = ['id', 'name', 'volume_size', 'start_time', 'tags', 'volume_id', 'volume_name', 'status']
        self.render_dict.update(dict(
            filter_keys=filter_keys,
            filter_fields=True,
            filters_form=SnapshotsFiltersForm(self.request, formdata=self.request.params or None),
            sort_keys=self.get_sort_keys(),
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.get_json_endpoint('snapshots_json'),
        ))
        return self.render_dict

    @view_config(route_name='snapshots_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def snapshots_delete(self):
        snapshot_id = self.request.params.get('snapshot_id')
        volume_id = self.request.params.get('volume_id')
        snapshot = self.get_snapshot(snapshot_id)
        # NOTE: could optimize by requiring snapshot name as param and avoid above CLC fetch
        snapshot_name = TaggedItemView.get_display_name(snapshot)
        location = self.get_redirect_location('snapshots')
        if volume_id:
            location = self.request.route_path('volume_snapshots', id=volume_id)
        if snapshot and self.delete_form.validate():
            with boto_error_handler(self.request, location):
                images_registered = self.get_images_registered(snapshot_id)
                if images_registered is not None:
                    for img in images_registered:
                        self.log_request(_(u"Deregistering image {0}").format(img.id))
                        img.deregister()
                    # Clear images cache
                    #ImagesView.invalidate_images_cache()
                self.log_request(_(u"Deleting snapshot {0}").format(snapshot_id))
                snapshot.delete()
                prefix = _(u'Successfully deleted snapshot')
                msg = '{prefix} {name}'.format(prefix=prefix, name=snapshot_name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            msg = _(u'Unable to delete snapshot')
            self.request.session.flash(msg, queue=Notification.ERROR)
            return HTTPFound(location=location)

    @view_config(route_name='snapshot_images_json', renderer='json', request_method='GET')
    def snapshot_images_json(self):
        id = self.request.matchdict.get('id')
        images = self.get_images_registered(id)
        if images is not None:
            image_list = []
            for img in images:
                image_list.append(dict(id=img.id, name=img.name))
            return dict(results=image_list)
        else:
            return dict(results=None)

    # same code is in SnapshotView below. Remove duplicate when GUI-662 refactoring happens
    def get_root_device_name(self, img):
        return img.root_device_name.replace('&#x2f;', '/').replace(
            '&#x2f;', '/') if img.root_device_name is not None else '/dev/sda'

    def get_images_registered(self, snap_id):
        ret = []
        images = self.conn.get_all_images(owners='self')
        for img in images:
            if img.block_device_mapping is not None:
                vol = img.block_device_mapping.get(self.get_root_device_name(img), None)
                if vol is not None and snap_id == vol.snapshot_id:
                    ret.append(img)
        return ret or None

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
        root_device_name = '/dev/sda' if self.cloud_type == 'euca' else '/dev/sda1'
        bdm[root_device_name] = root_vol
        location = self.get_redirect_location('snapshots')
        if snapshot and self.register_form.validate():
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Registering snapshot {0} as image {1}").format(snapshot_id, name))
                image_id = snapshot.connection.register_image(
                    name=name,
                    description=description,
                    root_device_name=root_device_name,
                    kernel_id=('windows' if reg_as_windows else None),
                    block_device_map=bdm
                )
                prefix = _(u'Successfully registered snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                # Clear images cache
                #ImagesView.invalidate_images_cache()
                location = self.request.route_path('image_view', id=image_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            # TODO: need validation error!
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

    @view_config(route_name='snapshots_json', renderer='json', request_method='POST')
    def snapshots_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        snapshots = []
        filtered_snapshots = self.filter_items(self.get_items())
        volume_ids = list(set([snapshot.volume_id for snapshot in filtered_snapshots]))
        volumes = self.conn.get_all_volumes(filters={'volume_id': volume_ids}) if self.conn else []
        for snapshot in filtered_snapshots:
            volume = [volume for volume in volumes if volume.id == snapshot.volume_id]
            volume_name = ''
            if volume:
                volume_name = TaggedItemView.get_display_name(volume[0], escapebraces=False)
            snapshots.append(dict(
                id=snapshot.id,
                description=snapshot.description,
                name=TaggedItemView.get_display_name(snapshot, escapebraces=False),
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
        if snapshot.status.lower() in ['completed', 'failed']:
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
        self.tagged_obj = self.snapshot
        with boto_error_handler(request, self.location):
            self.images_registered = self.get_images_registered(self.snapshot.id) if self.snapshot else None
        self.render_dict = dict(
            snapshot=self.snapshot,
            snapshot_description=self.snapshot.description if self.snapshot else '',
            registered=True if self.images_registered is not None else False,
            snapshot_name=self.snapshot_name,
            volume_name=self.volume_name,
            snapshot_form=self.snapshot_form,
            delete_form=self.delete_form,
            register_form=self.register_form,
            volume_count=self.get_volume_count()
        )

    def get_volume_count(self):
        if self.snapshot_form and self.snapshot_form.volume_id and self.snapshot_form.volume_id.choices:
            return len(self.snapshot_form.volume_id.choices)
        return 0

    def get_root_device_name(self, img):
        return img.root_device_name.replace('&#x2f;', '/').replace(
            '&#x2f;', '/') if img.root_device_name is not None else '/dev/sda'

    def get_images_registered(self, snap_id):
        ret = []
        images = self.conn.get_all_images(owners='self')
        for img in images:
            if img.block_device_mapping is not None:
                vol = img.block_device_mapping.get(self.get_root_device_name(img), None)
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
            location = self.request.route_path('snapshot_view', id=self.snapshot.id)
            with boto_error_handler(self.request, location):
                # Update tags
                self.update_tags()

                # Save Name tag
                name = self.request.params.get('name', '')
                self.update_name_tag(name)

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
            with boto_error_handler(self.request, self.request.route_path('snapshots')):
                self.log_request(_(u"Creating snapshot from volume {0}").format(volume_id))
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
            snapshot_name = TaggedItemView.get_display_name(self.snapshot)
            with boto_error_handler(self.request, self.request.route_path('snapshots')):
                if self.images_registered is not None:
                    for img in self.images_registered:
                        self.log_request(_(u"Deregistering image {0}").format(img.id))
                        img.deregister()
                    # Clear images cache
                    #ImagesView.invalidate_images_cache()
                self.log_request(_(u"Deleting snapshot {0}").format(self.snapshot.id))
                self.snapshot.delete()
                prefix = _(u'Successfully deleted snapshot')
                msg = '{prefix} {name}'.format(prefix=prefix, name=snapshot_name)
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
        root_device_name = '/dev/sda' if self.cloud_type == 'euca' else '/dev/sda1'
        bdm[root_device_name] = root_vol
        location = self.request.route_path('snapshot_view', id=snapshot_id)
        if self.snapshot and self.register_form.validate():
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Registering snapshot {0} as image {1}").format(snapshot_id, name))
                self.snapshot.connection.register_image(
                    name=name, description=description,
                    root_device_name=root_device_name,
                    kernel_id=('windows' if reg_as_windows else None),
                    block_device_map=bdm)
                prefix = _(u'Successfully registered snapshot')
                msg = '{prefix} {id}'.format(prefix=prefix, id=snapshot_id)
                # Clear images cache
                #ImagesView.invalidate_images_cache()
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
