# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS volumes

"""
import time

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.volumes import VolumeForm, DeleteVolumeForm
from ..models import LandingPageFilter, Notification
from ..views import LandingPageView, TaggedItemView


class VolumesView(LandingPageView):
    def __init__(self, request):
        super(VolumesView, self).__init__(request)
        self.items = self.get_items()
        self.initial_sort_key = '-create_time'
        self.prefix = '/volumes'

    def get_items(self):
        conn = self.get_connection()
        return conn.get_all_volumes() if conn else []

    @view_config(route_name='volumes', renderer='../templates/volumes/volumes.pt')
    def volumes_landing(self):
        json_items_endpoint = self.request.route_url('volumes_json')
        status_choices = sorted(set(item.status for item in self.items))
        zone_choices = sorted(set(item.zone for item in self.items))
        # Filter fields are passed to 'properties_filter_form' template macro to display filters at left
        self.filter_fields = [
            LandingPageFilter(key='status', name=_(u'Status'), choices=status_choices),
            LandingPageFilter(key='zone', name=_(u'Availability zone'), choices=zone_choices),
            # LandingPageFilter(key='tags', name='Tags'),
        ]
        more_filter_keys = ['id', 'instance', 'name', 'size', 'snapshot_id', 'create_time', 'tags']
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = [field.key for field in self.filter_fields] + more_filter_keys
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='-create_time', name=_(u'Create time')),
            dict(key='name', name=_(u'Name')),
            dict(key='status', name=_(u'Status')),
            dict(key='zone', name=_(u'Availability zone')),
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

    @view_config(route_name='volumes_json', renderer='json', request_method='GET')
    def volumes_json(self):
        volumes = []
        for volume in self.items:
            volumes.append(dict(
                create_time=volume.create_time,
                id=volume.id,
                instance=volume.attach_data.instance_id,
                name=volume.tags.get('Name', volume.id),
                snapshot_id=volume.snapshot_id,
                size=volume.size,
                status=volume.status,
                zone=volume.zone,
                tags=volume.tags,
            ))
        return dict(results=volumes)


class VolumeView(TaggedItemView):
    VIEW_TEMPLATE = '../templates/volumes/volume_view.pt'

    def __init__(self, request):
        super(VolumeView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection()
        self.volume = self.get_volume()
        self.volume_form = VolumeForm(
            self.request, volume=self.volume, conn=self.conn, formdata=self.request.params or None)
        self.delete_form = DeleteVolumeForm(self.request, formdata=self.request.params or None)
        self.tagged_obj = self.volume
        self.render_dict = dict(
            volume=self.volume,
            volume_form=self.volume_form,
            delete_form=self.delete_form,
        )

    @view_config(route_name='volume_view', renderer=VIEW_TEMPLATE, request_method='GET')
    def volume_view(self):
        return self.render_dict

    @view_config(route_name='volume_update', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_update(self):
        if self.volume and self.volume_form.validate():
            # Update tags
            self.update_tags()

            location = self.request.route_url('volume_view', id=self.volume.id)
            msg = _(u'Successfully modified volume')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='volume_create', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_create(self):
        if self.volume_form.validate():
            name = self.request.params.get('name', '')
            size = int(self.request.params.get('size', 1))
            zone = self.request.params.get('zone')
            snapshot_id = self.request.params.get('snapshot_id')
            kwargs = dict(size=size, zone=zone)
            if snapshot_id:
                kwargs['snapshot_id'] = snapshot_id
            volume = self.conn.create_volume(**kwargs)

            # Add name tag
            if name:
                volume.add_tag('Name', name)

            location = self.request.route_url('volumes')
            prefix = _(u'Successfully created volume')
            msg = '{prefix} {volume}'.format(prefix=prefix, volume=volume.id)
            self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='volume_delete', renderer=VIEW_TEMPLATE, request_method='POST')
    def volume_delete(self):
        if self.volume and self.delete_form.validate():
            self.volume.delete()
            time.sleep(1)
            location = self.request.route_url('volume_view', id=self.volume.id)
            msg = _(u'Successfully sent delete volume request.  It may take a moment to delete the volume.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict

    def get_volume(self):
        volume_id = self.request.matchdict.get('id')
        if volume_id:
            volumes_list = self.conn.get_all_volumes(volume_ids=[volume_id])
            return volumes_list[0] if volumes_list else None
        return None

