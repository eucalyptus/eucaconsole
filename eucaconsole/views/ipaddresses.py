# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Elastic IP Addresses

"""
from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.ipaddresses import (
    AllocateIPsForm, AssociateIPForm, DisassociateIPForm, ReleaseIPForm, IPAddressesFiltersForm)
from ..models import Notification
from ..views import LandingPageView, TaggedItemView, BaseView


class IPAddressesView(LandingPageView):
    """Views for IP Addresses landing page"""
    VIEW_TEMPLATE = '../templates/ipaddresses/ipaddresses.pt'

    def __init__(self, request):
        super(IPAddressesView, self).__init__(request)
        self.initial_sort_key = 'public_ip'
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/ipaddresses'
        self.conn = self.get_connection()
        self.allocate_form = AllocateIPsForm(self.request, formdata=self.request.params or None)
        self.associate_form = AssociateIPForm(self.request, conn=self.conn, formdata=self.request.params or None)
        self.disassociate_form = DisassociateIPForm(self.request, formdata=self.request.params or None)
        self.release_form = ReleaseIPForm(self.request, formdata=self.request.params or None)
        self.filters_form = IPAddressesFiltersForm(self.request, conn=self.conn, formdata=self.request.params or None)
        self.json_items_endpoint = self.get_json_endpoint('ipaddresses_json')
        self.sort_keys = self.get_sort_keys()
        self.location = self.get_redirect_location('ipaddresses')
        self.filter_keys = ['public_ip', 'instance_id']
        self.render_dict = dict(
            filter_fields=True,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            allocate_form=self.allocate_form,
            associate_form=self.associate_form,
            disassociate_form=self.disassociate_form,
            release_form=self.release_form,
            filters_form=self.filters_form,
        )

    @view_config(route_name='ipaddresses', renderer=VIEW_TEMPLATE)
    def ipaddresses_landing(self):
        # sort_keys are passed to sorting drop-down
        # Handle Allocate IP addresses form
        if self.request.method == 'POST':
            if self.allocate_form.validate():
                new_ips = []
                ipcount = int(self.request.params.get('ipcount', 0))
                try:
                    for i in xrange(ipcount):
                        new_ip = self.conn.allocate_address()
                        new_ips.append(new_ip.public_ip)
                    prefix = _(u'Successfully allocated IPs')
                    ips = ', '.join(new_ips)
                    msg = u'{prefix} {ips}'.format(prefix=prefix, ips=ips)
                    self.request.session.flash(msg, queue=Notification.SUCCESS)
                except BotoServerError as err:
                    self.sendErrorResponse(err)
                return HTTPFound(location=self.location)
        return self.render_dict

    @view_config(route_name='ipaddresses_associate', request_method="POST")
    def ipaddresses_associate(self):
        if self.associate_form.validate():
            instance_id = self.request.params.get('instance_id')
            public_ip = self.request.params.get('public_ip')
            try:
                elastic_ip = self.get_elastic_ip(public_ip)
                elastic_ip.associate(instance_id)
                template = _(u'Successfully associated IP {ip} with instance {instance}')
                msg = template.format(ip=elastic_ip.public_ip, instance=instance_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            except BotoServerError as err:
                self.sendErrorResponse(err)
        else:
            msg = _(u'Unable to associate IP with instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='ipaddresses_disassociate', request_method="POST")
    def ipaddresses_disassociate(self):
        if self.disassociate_form.validate():
            public_ip = self.request.params.get('public_ip')
            try:
                #TODO: re-write to not fetch eip prior to operation
                elastic_ip = self.get_elastic_ip(public_ip)
                elastic_ip.disassociate()
                template = _(u'Successfully disassociated IP {ip} from instance {instance}')
                msg = template.format(ip=elastic_ip.public_ip, instance=elastic_ip.instance_id)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            except BotoServerError as err:
                self.sendErrorResponse(err)
        else:
            msg = _(u'Unable to disassociate IP from instance')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    @view_config(route_name='ipaddresses_release', request_method="POST")
    def ipaddresses_release(self):
        if self.release_form.validate():
            public_ip = self.request.params.get('public_ip')
            try:
                #TODO: re-write to not fetch eip prior to operation
                elastic_ip = self.get_elastic_ip(public_ip)
                elastic_ip.release()
                template = _(u'Successfully released {ip} to the cloud')
                msg = template.format(ip=elastic_ip.public_ip)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            except BotoServerError as err:
                self.sendErrorResponse(err)
        else:
            msg = _(u'Unable to release IP address')
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=self.location)

    def get_elastic_ip(self, public_ip):
        addresses_param = [public_ip]
        ip_addresses = self.conn.get_all_addresses(addresses=addresses_param)
        elastic_ip = ip_addresses[0] if ip_addresses else None
        return elastic_ip

    @staticmethod
    def get_sort_keys():
        """sort_keys are passed to sorting drop-down on landing page"""
        return [
            dict(key='public_ip', name=_(u'IP Address')),
            dict(key='instance_id', name=_(u'Instance')),
        ]


class IPAddressesJsonView(LandingPageView):
    def __init__(self, request):
        super(IPAddressesJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='ipaddresses_json', renderer='json', request_method='GET')
    def ipaddresses_json(self):
        ipaddresses = []
        try:
            items = self.get_items()
            if self.request.params.getall('assignment'):
                items = self.filter_by_assignment(items)
            instances = self.get_instances(items)
            for address in items:
                ipaddresses.append(dict(
                    public_ip=address.public_ip,
                    instance_id=address.instance_id,
                    instance_name=TaggedItemView.get_display_name(
                        instances[address.instance_id]) if address.instance_id else address.instance_id,
                    domain=address.domain,
                ))
            return dict(results=ipaddresses)
        except BotoServerError as err:
            return self.getJSONErrorResponse(err)

    def get_items(self):
        return self.conn.get_all_addresses() if self.conn else []

    # return dictionary of instances (by their id)
    def get_instances(self, ipaddresses):
        ids = []
        for ip in ipaddresses:
            if ip.instance_id:
                ids.append(ip.instance_id)
        instances = self.conn.get_only_instances(ids)
        ret = {}
        for inst in instances:
            ret[inst.id] = inst
        return ret

    def filter_by_assignment(self, items):
        filtered_items = []
        for item in items:
            for assignment in self.request.params.getall('assignment'):
                if (assignment and item.instance_id) or (not assignment and not item.instance_id):
                    filtered_items.append(item)
        return filtered_items


class IPAddressView(BaseView):
    """Views for actions on single IP Address"""
    VIEW_TEMPLATE = '../templates/ipaddresses/ipaddress_view.pt'

    def __init__(self, request):
        super(IPAddressView, self).__init__(request)
        self.conn = self.get_connection()
        self.elastic_ip = self.get_elastic_ip()
        self.instance = self.get_instance()
        self.associate_form = AssociateIPForm(self.request, conn=self.conn, formdata=self.request.params or None)
        self.disassociate_form = DisassociateIPForm(self.request, formdata=self.request.params or None)
        self.release_form = ReleaseIPForm(self.request, formdata=self.request.params or None)
        if self.elastic_ip:
            self.elastic_ip.instance_name = ''
            if self.instance:
                self.elastic_ip.instance_name = TaggedItemView.get_display_name(self.instance)
        self.render_dict = dict(
            eip=self.elastic_ip,
            associate_form=self.associate_form,
            disassociate_form=self.disassociate_form,
            release_form=self.release_form,
        )

    @view_config(route_name='ipaddress_view', renderer=VIEW_TEMPLATE)
    def ipaddress_view(self):
        return self.render_dict

    @view_config(route_name='ipaddress_associate', request_method="POST")
    def ipaddress_associate(self):
        if self.associate_form.validate():
            instance_id = self.request.params.get('instance_id')
            location = self.request.route_path('ipaddresses')
            try:
                self.elastic_ip.associate(instance_id)
                msg = _(u'Successfully associated IP {ip} with instance {instance}')
                notification_msg = msg.format(ip=self.elastic_ip.public_ip, instance=instance_id)
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            except BotoServerError as err:
                self.sendErrorResponse(err)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='ipaddress_disassociate', renderer=VIEW_TEMPLATE, request_method="POST")
    def ipaddress_disassociate(self):
        if self.disassociate_form.validate():
            location = self.request.route_path('ipaddresses')
            try:
                #TODO: re-write to not fetch eip prior to operation
                self.elastic_ip.disassociate()
                msg = _(u'Successfully disassociated IP {ip} from instance {instance}')
                notification_msg = msg.format(ip=self.elastic_ip.public_ip, instance=self.elastic_ip.instance_id)
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            except BotoServerError as err:
                self.sendErrorResponse(err)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='ipaddress_release', renderer=VIEW_TEMPLATE, request_method="POST")
    def ipaddress_release(self):
        if self.release_form.validate():
            location = self.request.route_path('ipaddresses')
            try:
                #TODO: re-write to not fetch eip prior to operation
                self.elastic_ip.release()
                msg = _(u'Successfully released {ip} to the cloud')
                notification_msg = msg.format(ip=self.elastic_ip.public_ip)
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            except BotoServerError as err:
                self.sendErrorResponse(err)
            return HTTPFound(location=location)
        return self.render_dict

    def get_elastic_ip(self):
        address_param = self.request.matchdict.get('public_ip')
        addresses_param = [address_param]
        ip_addresses = []
        elastic_ip = None
        try:
            if self.conn:
                ip_addresses = self.conn.get_all_addresses(addresses=addresses_param)
            elastic_ip = ip_addresses[0] if ip_addresses else None
        except BotoServerError as err:
            response = self.getJSONErrorResponse(err) # invokes 403 checking
        return elastic_ip

    def get_instance(self):
        if self.elastic_ip and self.elastic_ip.instance_id:
            try:
                instances = self.conn.get_only_instances(instance_ids=[self.elastic_ip.instance_id])
                return instances[0] if instances else None
            except BotoServerError as err:
                response = self.getJSONErrorResponse(err) # invokes 403 checking
        return None

