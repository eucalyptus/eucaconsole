# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Elastic IP Addresses

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..forms.ipaddresses import AllocateIPsForm, AssociateIPForm, DisassociateIPForm, ReleaseIPForm
from ..models import Notification
from ..views import BaseView, LandingPageView


class IPAddressesView(LandingPageView):
    """Views for IP Addresses landing page"""
    VIEW_TEMPLATE = '../templates/ipaddresses/ipaddresses.pt'

    def __init__(self, request):
        super(IPAddressesView, self).__init__(request)
        self.initial_sort_key = 'public_ip'
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/ipaddresses'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default
        self.conn = self.get_connection()
        self.allocate_form = AllocateIPsForm(self.request, formdata=self.request.params or None)
        self.associate_form = AssociateIPForm(self.request, conn=self.conn, formdata=self.request.params or None)
        self.disassociate_form = DisassociateIPForm(self.request, formdata=self.request.params or None)
        self.release_form = ReleaseIPForm(self.request, formdata=self.request.params or None)
        self.json_items_endpoint = self.request.route_url('ipaddresses_json')
        self.sort_keys = self.get_sort_keys()
        self.location = self.get_redirect_location()
        self.filter_keys = ['public_ip', 'instance_id']
        self.render_dict = dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            allocate_form=self.allocate_form,
            associate_form=self.associate_form,
            disassociate_form=self.disassociate_form,
            release_form=self.release_form
        )

    @view_config(route_name='ipaddresses', renderer=VIEW_TEMPLATE)
    def ipaddresses_landing(self):
        # sort_keys are passed to sorting drop-down
        # Handle Allocate IP addresses form
        if self.request.method == 'POST':
            if self.allocate_form.validate():
                new_ips = []
                ipcount = int(self.request.params.get('ipcount', 0))
                for i in xrange(ipcount):
                    new_ip = self.conn.allocate_address()
                    new_ips.append(new_ip.public_ip)
                prefix = _(u'Successfully allocated IPs')
                ips = ', '.join(new_ips)
                notification_msg = u'{prefix} {ips}'.format(prefix=prefix, ips=ips)
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
                return HTTPFound(location=self.location)
        render_dict = self.render_dict
        render_dict['sort_keys'] = self.sort_keys
        return render_dict

    @view_config(route_name='ipaddresses_json', renderer='json', request_method='GET')
    def ipaddresses_json(self):
        ipaddresses = []
        for address in self.get_items():
            ipaddresses.append(dict(
                public_ip=address.public_ip,
                instance_id=address.instance_id,
                domain=address.domain,
            ))
        return dict(results=ipaddresses)

    @view_config(route_name='ipaddresses_associate', request_method="POST")
    def ipaddresses_associate(self):
        if self.associate_form.validate():
            instance_id = self.request.params.get('instance_id')
            public_ip = self.request.params.get('public_ip')
            elastic_ip = self.get_elastic_ip(public_ip)
            elastic_ip.associate(instance_id)
            template = _(u'Successfully associated IP {ip} with instance {instance}')
            msg = template.format(ip=elastic_ip.public_ip, instance=instance_id)
            queue = Notification.SUCCESS
        else:
            msg = _(u'Unable to associate IP with instance')
            queue = Notification.ERROR
        self.request.session.flash(msg, queue=queue)
        return HTTPFound(location=self.location)

    @view_config(route_name='ipaddresses_disassociate', request_method="POST")
    def ipaddresses_disassociate(self):
        if self.disassociate_form.validate():
            public_ip = self.request.params.get('public_ip')
            elastic_ip = self.get_elastic_ip(public_ip)
            elastic_ip.disassociate()
            template = _(u'Successfully disassociated IP {ip} from instance {instance}')
            msg = template.format(ip=elastic_ip.public_ip, instance=elastic_ip.instance_id)
            queue = Notification.SUCCESS
        else:
            msg = _(u'Unable to disassociate IP from instance')
            queue = Notification.ERROR
        self.request.session.flash(msg, queue=queue)
        return HTTPFound(location=self.location)

    @view_config(route_name='ipaddresses_release', request_method="POST")
    def ipaddresses_release(self):
        if self.release_form.validate():
            public_ip = self.request.params.get('public_ip')
            elastic_ip = self.get_elastic_ip(public_ip)
            elastic_ip.release()
            template = _(u'Successfully released {ip} to the cloud')
            msg = template.format(ip=elastic_ip.public_ip)
            queue = Notification.SUCCESS
        else:
            msg = _(u'Unable to release IP address')
            queue = Notification.ERROR
        self.request.session.flash(msg, queue=queue)
        return HTTPFound(location=self.location)

    def get_items(self):
        return self.conn.get_all_addresses() if self.conn else []

    def get_elastic_ip(self, public_ip):
        addresses_param = [public_ip]
        ip_addresses = self.conn.get_all_addresses(addresses=addresses_param)
        elastic_ip = ip_addresses[0] if ip_addresses else None
        return elastic_ip

    def get_redirect_location(self):
        display_type = self.request.params.get('display', self.display_type)
        return '{}?display={}'.format(self.request.route_url('ipaddresses'), display_type)

    @staticmethod
    def get_sort_keys():
        """sort_keys are passed to sorting drop-down on landing page"""
        return [
            dict(key='public_ip', name=_(u'IP Address')),
            dict(key='instance_id', name=_(u'Instance')),
        ]


class IPAddressView(BaseView):
    """Views for actions on single IP Address"""
    VIEW_TEMPLATE = '../templates/ipaddresses/ipaddress_view.pt'

    def __init__(self, request):
        super(IPAddressView, self).__init__(request)
        self.conn = self.get_connection()
        self.elastic_ip = self.get_elastic_ip()
        self.associate_form = AssociateIPForm(self.request, conn=self.conn, formdata=self.request.params)
        self.disassociate_form = DisassociateIPForm(self.request, formdata=self.request.params)
        self.release_form = ReleaseIPForm(self.request, formdata=self.request.params)
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
            self.elastic_ip.associate(instance_id)
            location = self.request.route_url('ipaddresses')
            msg = _(u'Successfully associated IP {ip} with instance {instance}')
            notification_msg = msg.format(ip=self.elastic_ip.public_ip, instance=instance_id)
            self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='ipaddress_disassociate', renderer=VIEW_TEMPLATE, request_method="POST")
    def ipaddress_disassociate(self):
        if self.disassociate_form.validate():
            self.elastic_ip.disassociate()
            location = self.request.route_url('ipaddresses')
            msg = _(u'Successfully disassociated IP {ip} from instance {instance}')
            notification_msg = msg.format(ip=self.elastic_ip.public_ip, instance=self.elastic_ip.instance_id)
            self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    @view_config(route_name='ipaddress_release', renderer=VIEW_TEMPLATE, request_method="POST")
    def ipaddress_release(self):
        if self.release_form.validate():
            self.elastic_ip.release()
            location = self.request.route_url('ipaddresses')
            msg = _(u'Successfully released {ip} to the cloud')
            notification_msg = msg.format(ip=self.elastic_ip.public_ip)
            self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        return self.render_dict

    def get_elastic_ip(self):
        address_param = self.request.matchdict.get('public_ip')
        addresses_param = [address_param]
        ip_addresses = self.conn.get_all_addresses(addresses=addresses_param)
        elastic_ip = ip_addresses[0] if ip_addresses else None
        return elastic_ip

