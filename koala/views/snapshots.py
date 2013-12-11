# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS snapshots

"""
import simplejson as json
import time

from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.snapshots import SnapshotForm, DeleteSnapshotForm
from ..models import LandingPageFilter, Notification
from ..views import LandingPageView, TaggedItemView, BaseView


class SnapshotsView(LandingPageView):
    def __init__(self, request):
        super(SnapshotsView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-start_time'
        self.prefix = '/snapshots'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_all_snapshots(owner='self') if conn else []

    @view_config(route_name='snapshots', renderer='../templates/snapshots/snapshots.pt')
    def snapshots_landing(self):
        json_items_endpoint = self.request.route_url('snapshots_json')
        status_choices = sorted(set(item.status for item in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name=_(u'Status'), choices=status_choices),
        ]
        more_filter_keys = ['id', 'name', 'volume_size', 'start_time', 'tags', 'volume_id']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-start_time', name=_(u'Start time')),
            dict(key='volume_size', name=_(u'Size')),
            dict(key='name', name=_(u'Name')),
            dict(key='status', name=_(u'Status')),
            dict(key='volume_id', name=_(u'Volume ID')),
        ]

        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
        )

    @view_config(route_name='snapshots_json', renderer='json', request_method='GET')
    def snapshots_json(self):
        snapshots = []
        for snapshot in self.items:
            snapshots.append(dict(
                id=snapshot.id,
                description=snapshot.description,
                name=snapshot.tags.get('Name', snapshot.id),
                start_time=snapshot.start_time,
                status=snapshot.status,
                tags=TaggedItemView.get_tags_display(snapshot.tags),
                volume_id=snapshot.volume_id,
                volume_size=snapshot.volume_size,
            ))
        return dict(results=snapshots)


class SnapshotView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/snapshots/snapshot_view.pt'

    def __init__(self, request):
        super(SnapshotView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.snapshot = self.get_snapshot()
        self.snapshot_form = SnapshotForm(
            self.request, snapshot=self.snapshot, conn=self.conn, formdata=self.request.params or None)
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.snapshot
        self.render_dict = dict(
            snapshot=self.snapshot,
            snapshot_form=self.snapshot_form,
            delete_form=self.delete_form,
        )

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

