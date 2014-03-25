# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS volumes

"""
from dateutil import parser
import simplejson as json

from boto.exception import BotoServerError
from boto.ec2.snapshot import Snapshot

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.volumes import (
    VolumeForm, DeleteVolumeForm, CreateSnapshotForm, DeleteSnapshotForm,
    RegisterSnapshotForm, AttachForm, DetachForm, VolumesFiltersForm)
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, BaseView
from . import boto_error_handler


class BaseVolumeView(BaseView):
    """Base class for volume-related views"""
    def __init__(self, request):
        super(BaseVolumeView, self).__init__(request)
        self.conn = self.get_connection()

    def get_volume(self, volume_id=None):
        volume_id = volume_id or self.request.matchdict.get('id')
        if volume_id and volume_id != 'new':
            try:
                volumes_list = self.conn.get_all_volumes(volume_ids=[volume_id])
                return volumes_list[0] if volumes_list else None
            except BotoServerError as err:
                return None
        return None


class VolumesView(LandingPageView, BaseVolumeView):
    VIEW_TEMPLATE = '../templates/volumes/volumes.pt'

    def __init__(self, request):
        super(VolumesView, self).__init__(request)
        self.conn = self.get_connection()
        self.initial_sort_key = '-create_time'
        self.prefix = '/volumes'
        self.json_items_endpoint = self.get_json_endpoint('volumes_json')
        self.location = self.get_redirect_location('volumes')
        with boto_error_handler(request, self.location):
            self.instances = self.get_instances_by_state(self.conn.get_only_instances() if self.conn else [], "running")
        self.delete_form = DeleteVolumeForm(self.request, formdata=self.request.params or None)
        self.attach_form = AttachForm(self.request, instances=self.instances, formdata=self.request.params or None)
        self.detach_form = DetachForm(self.request, formdata=self.request.params or None)
        self.filters_form = VolumesFiltersForm(self.request, conn=self.conn, formdata=self.request.params or None)
        self.render_dict = dict(
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            filters_form=self.filters_form,
        )

    @view_config(route_name='volumes', renderer=VIEW_TEMPLATE)
    def volumes_landing(self):
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        filter_keys = [
            'attach_status', 'create_time', 'id', 'instance', 'name', 'instance_name',
            'size', 'snapshot_id', 'status', 'tags', 'zone'
        ]
        # filter_keys are passed to client-side filtering in search box
        self.render_dict.update(dict(
            filter_fields=True,
            sort_keys=self.get_sort_keys(),
            filter_keys=filter_keys,
            json_items_endpoint=self.json_items_endpoint,
            attach_form=self.attach_form,
            detach_form=self.detach_form,
            delete_form=self.delete_form,
            instances_by_zone=json.dumps(self.get_instances_by_zone(self.instances)),
        ))
        return self.render_dict

    @view_config(route_name='volumes_delete', request_method='POST')
    def volumes_delete(self):
        volume_id = self.request.params.get('volume_id')
        volume = self.get_volume(volume_id)
        if volume and self.delete_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Deleting volume {0}").format(volume_id))
                volume.delete()
                msg = _(u'Successfully sent delete volume request.  It may take a moment to delete the volume.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to delete volume.')  # TODO Pull in form validation error messages here
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='volumes_attach', request_method='POST')
    def volumes_attach(self):
        volume_id = self.request.params.get('volume_id')
        volume = self.get_volume(volume_id)
        if volume and self.attach_form.validate():
            instance_id = self.request.params.get('instance_id')
            device = self.request.params.get('device')
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Attaching volume {0} to {1} as {2}").format(volume_id, instance_id, device))
                volume.attach(instance_id, device)
                msg = _(u'Successfully sent request to attach volume.  It may take a moment to attach to instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to attach volume.')  # TODO Pull in form validation error messages here
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='volumes_detach', request_method='POST')
    def volumes_detach(self):
        volume_id = self.request.params.get('volume_id')
        volume = self.get_volume(volume_id)
        if self.detach_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Detaching volume {0} from {1}").format(volume_id, volume.attach_data.instance_id))
                volume.detach()
                msg = _(u'Request successfully submitted.  It may take a moment to detach the volume.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to attach volume.')  # TODO Pull in form validation error messages here
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @staticmethod
    def get_instances_by_zone(instances):
        zones = set(instance.placement for instance in instances)
        instances_by_zone = {}
        for zone in zones:
            zone_instances = []
            for instance in instances:
                if instance.placement == zone:
                    instance_name = TaggedItemView.get_display_name(instance)
                    zone_instances.append({'id': instance.id, 'name': instance_name})
            instances_by_zone[zone] = zone_instances
        return instances_by_zone

    @staticmethod
    def get_instances_by_state(instances, state="running"):
        instances_by_state = []
        for instance in instances:
            if instance.state == state:
                instances_by_state.append(instance)
        return instances_by_state

    @staticmethod
    def get_sort_keys():
        """sort_keys are passed to sorting drop-down on landing page"""
        return [
            dict(key='create_time', name=_(u'Creation time: Oldest to Newest')),
            dict(key='-create_time', name=_(u'Creation time: Newest to Oldest')),
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='status', name=_(u'Status')),
            dict(key='zone', name=_(u'Availability zone')),
        ]


class VolumesJsonView(LandingPageView):
    def __init__(self, request):
        super(VolumesJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='volumes_json', renderer='json', request_method='GET')
    def volumes_json(self):
        volumes = []
        transitional_states = ['attaching', 'detaching', 'creating', 'deleting']
        filters = {}
        availability_zone_param = self.request.params.getall('zone')
        if availability_zone_param:
            filters.update({'availability-zone': availability_zone_param})
        # Don't filter by these request params in Python, as they're included in the "filters" params sent to the CLC
        # Note: the choices are from attributes in VolumesFiltersForm
        ignore_params = ['zone']
        with boto_error_handler(self.request):
            filtered_items = self.filter_items(self.get_items(filters=filters), ignore=ignore_params)
            instance_ids = list(set([
                vol.attach_data.instance_id for vol in filtered_items if vol.attach_data.instance_id is not None]))
            volume_ids = [volume.id for volume in filtered_items]
            snapshots = self.conn.get_all_snapshots(filters={'volume-id': volume_ids}) if self.conn else []
            instances = self.conn.get_only_instances(instance_ids=instance_ids) if self.conn else []

            for volume in filtered_items:
                status = volume.status
                attach_status = volume.attach_data.status
                instance_name = None
                if volume.attach_data is not None and volume.attach_data.instance_id is not None:
                    instance = [inst for inst in instances if inst.id == volume.attach_data.instance_id][0]
                    instance_name = TaggedItemView.get_display_name(instance)
                volumes.append(dict(
                    create_time=volume.create_time,
                    id=volume.id,
                    instance=volume.attach_data.instance_id,
                    device=volume.attach_data.device,
                    instance_name=instance_name,
                    name=TaggedItemView.get_display_name(volume),
                    snapshots=len([snap.id for snap in snapshots if snap.volume_id == volume.id]),
                    size=volume.size,
                    status=status,
                    attach_status=attach_status,
                    zone=volume.zone,
                    tags=TaggedItemView.get_tags_display(volume.tags),
                    transitional=status in transitional_states or attach_status in transitional_states,
                ))
            return dict(results=volumes)

    def get_items(self, filters=None):
        return self.conn.get_all_volumes(filters=filters) if self.conn else []


class VolumeView(TaggedItemView, BaseVolumeView):
    VIEW_TEMPLATE = '../templates/volumes/volume_view.pt'

    def __init__(self, request):
        super(VolumeView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.location = self.request.route_path('volume_view', id=self.request.matchdict.get('id'))
        with boto_error_handler(request, self.location):
            self.volume = self.get_volume()
            snapshots = self.conn.get_all_snapshots() if self.conn else []
            zones = self.conn.get_all_zones() if self.conn else []
            instances = self.conn.get_only_instances() if self.conn else []
        self.volume_form = VolumeForm(
            self.request, conn=self.conn, volume=self.volume, snapshots=snapshots,
            zones=zones, formdata=self.request.params or None)
        self.delete_form = DeleteVolumeForm(self.request, formdata=self.request.params or None)
        self.attach_form = AttachForm(
            self.request, instances=instances, volume=self.volume, formdata=self.request.params or None)
        self.detach_form = DetachForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.volume
        self.attach_data = self.volume.attach_data if self.volume else None
        self.volume_name = self.get_volume_name()
        self.create_time = self.get_create_time()
        self.instance_name = None
        if self.attach_data is not None and self.attach_data.instance_id is not None:
            instance = self.get_instance(self.attach_data.instance_id)
            self.instance_name = TaggedItemView.get_display_name(instance)
        self.render_dict = dict(
            volume=self.volume,
            volume_name=self.volume_name,
            volume_create_time=self.create_time,
            instance_name=self.instance_name,
            device_name=self.attach_data.device if self.attach_data else None,
            attachment_time=self.get_attachment_time(),
            volume_form=self.volume_form,
            delete_form=self.delete_form,
            attach_form=self.attach_form,
            detach_form=self.detach_form,
        )

    @view_config(route_name='volume_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def volume_view(self):
        if self.volume is None and self.request.matchdict.get('id') != 'new':
            raise HTTPNotFound
        return self.render_dict

    def get_create_time(self):
        """Returns volume create time as a python datetime.datetime object"""
        if self.volume and self.volume.create_time:
            return parser.parse(self.volume.create_time)
        return None

    def get_attachment_time(self):
        """Returns volume attach time as a python datetime.datetime object"""
        if self.volume and self.attach_data.attach_time:
            return parser.parse(self.attach_data.attach_time)
        return None

    @view_config(route_name='volume_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_update(self):
        if self.volume and self.volume_form.validate():
            # Update tags
            location = self.request.route_path('volume_view', id=self.volume.id)
            with boto_error_handler(self.request, location):
                self.update_tags()

                msg = _(u'Successfully modified volume')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.volume_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='volume_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_create(self):
        if self.volume_form.validate():
            name = self.request.params.get('name', '')
            tags_json = self.request.params.get('tags')
            size = int(self.request.params.get('size', 1))
            zone = self.request.params.get('zone')
            snapshot_id = self.request.params.get('snapshot_id')
            kwargs = dict(size=size, zone=zone)
            if snapshot_id:
                snapshot = self.get_snapshot(snapshot_id)
                kwargs['snapshot'] = snapshot
            with boto_error_handler(self.request, self.request.route_path('volumes')):
                self.log_request(_(u"Creating volume (size={0}, zone={1}, snapshot_id={2})").format(size, zone, snapshot_id))
                volume = self.conn.create_volume(**kwargs)
                # Add name tag
                if name:
                    volume.add_tag('Name', name)
                if tags_json:
                    tags = json.loads(tags_json)
                    for tagname, tagvalue in tags.items():
                        volume.add_tag(tagname, tagvalue)
                msg = _(u'Successfully sent create volume request.  It may take a moment to create the volume.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                location = self.request.route_path('volume_view', id=volume.id)
                return HTTPFound(location=location)
        else:
            self.request.error_messages = self.volume_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='volume_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_delete(self):
        if self.volume and self.delete_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Deleting volume {0}").format(self.volume.id))
                self.volume.delete()
                msg = _(u'Successfully sent delete volume request.  It may take a moment to delete the volume.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            location = self.request.route_path('volume_view', id=self.volume.id)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.volume_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='volume_attach', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_attach(self):
        if self.volume and self.attach_form.validate():
            instance_id = self.request.params.get('instance_id')
            device = self.request.params.get('device')
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Attaching volume {0} to {1} as {2}").format(self.volume.id, instance_id, device))
                self.volume.attach(instance_id, device)
                msg = _(u'Successfully sent request to attach volume.  It may take a moment to attach to instance.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            location = self.request.route_path('volume_view', id=self.volume.id)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.volume_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='volume_detach', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_detach(self):
        if self.detach_form.validate():
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Detaching volume {0} from {1}").format(self.volume.id, self.volume.attach_data.instance_id))
                self.volume.detach()
                msg = _(u'Request successfully submitted.  It may take a moment to detach the volume.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            location = self.request.route_path('volume_view', id=self.volume.id)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.volume_form.get_errors_list()
        return self.render_dict

    def get_snapshot(self, snapshot_id):
        snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
        return snapshots_list[0] if snapshots_list else None

    def get_instance(self, instance_id):
        if instance_id:
            instances_list = self.conn.get_only_instances(instance_ids=[instance_id])
            return instances_list[0] if instances_list else None
        return None

    def get_volume_name(self):
        if self.volume:
            return TaggedItemView.get_display_name(self.volume)
        return None


class VolumeStateView(BaseVolumeView):
    def __init__(self, request):
        super(VolumeStateView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.volume = self.get_volume()

    @view_config(route_name='volume_state_json', renderer='json', request_method='GET')
    def volume_state_json(self):
        """Return current volume status"""
        volume_status = self.volume.status
        attach_status = self.volume.attach_data.status
        attach_device = self.volume.attach_data.device
        attach_time = self.volume.attach_data.attach_time
        return dict(
            results=dict(volume_status=volume_status,
                         attach_status=attach_status,
                         attach_device=attach_device,
                         attach_time=attach_time)
        )


class VolumeSnapshotsView(BaseVolumeView):
    VIEW_TEMPLATE = '../templates/volumes/volume_snapshots.pt'

    def __init__(self, request):
        super(VolumeSnapshotsView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.location = self.request.route_path('volume_snapshots', id=self.request.matchdict.get('id'))
        with boto_error_handler(request, self.location):
            self.volume = self.get_volume()
        self.tagged_obj = self.volume
        self.volume_name = TaggedItemView.get_display_name(self.volume)
        self.add_form = None
        self.create_form = CreateSnapshotForm(self.request, formdata=self.request.params or None)
        self.delete_form = DeleteSnapshotForm(self.request, formdata=self.request.params or None)
        self.register_form = RegisterSnapshotForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            volume=self.volume,
            volume_name=self.volume_name,
            create_form=self.create_form,
            delete_form=self.delete_form,
            register_form=self.register_form,
        )

    @view_config(route_name='volume_snapshots', renderer=VIEW_TEMPLATE, request_method='GET')
    def volume_snapshots(self):
        if self.volume is None:
            raise HTTPNotFound()
        return self.render_dict

    @view_config(route_name='volume_snapshots_json', renderer='json', request_method='GET')
    def volume_snapshots_json(self):
        with boto_error_handler(self.request):
            snapshots = []
            for snapshot in self.volume.snapshots():
                delete_form_action = self.request.route_path(
                    'volume_snapshot_delete', id=self.volume.id, snapshot_id=snapshot.id)
                snapshots.append(dict(
                    id=snapshot.id,
                    name=TaggedItemView.get_display_name(snapshot),
                    progress=snapshot.progress,
                    volume_size=self.volume.size,
                    start_time=snapshot.start_time,
                    description=snapshot.description,
                    status=snapshot.status,
                    delete_form_action=delete_form_action,
                ))
            return dict(results=snapshots)

    @view_config(route_name='volume_snapshot_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_snapshot_create(self):
        if self.create_form.validate():
            name = self.request.params.get('name')
            description = self.request.params.get('description')
            tags_json = self.request.params.get('tags')
            with boto_error_handler(self.request, self.location):
                self.log_request(_(u"Creating snapshot from volume {0}").format(self.volume.id))
                params = {'VolumeId': self.volume.id}
                if description:
                    params['Description'] = description[0:255]
                snapshot = self.volume.connection.get_object('CreateSnapshot', params, Snapshot, verb='POST')
                
                # Add name tag
                if name:
                    snapshot.add_tag('Name', name)
                if tags_json:
                    tags = json.loads(tags_json)
                    for tagname, tagvalue in tags.items():
                        snapshot.add_tag(tagname, tagvalue)
                msg = _(u'Successfully sent create snapshot request.  It may take a moment to create the snapshot.')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            location = self.request.route_path('volume_snapshots', id=self.volume.id)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    @view_config(route_name='volume_snapshot_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_snapshot_delete(self):
        if self.delete_form.validate():
            volume_id = self.request.matchdict.get('id')
            snapshot_id = self.request.matchdict.get('snapshot_id')
            if volume_id and snapshot_id:
                snapshot = self.get_snapshot(snapshot_id)
                with boto_error_handler(self.request, self.location):
                    snapshot.delete()
                    msg = _(u'Successfully deleted the snapshot.')
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                location = self.request.route_path('volume_snapshots', id=self.volume.id)
                return HTTPFound(location=location)
        return self.render_dict

    def get_snapshot(self, snapshot_id):
        snapshots_list = self.conn.get_all_snapshots(snapshot_ids=[snapshot_id])
        return snapshots_list[0] if snapshots_list else None
