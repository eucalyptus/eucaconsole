# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS Elastic IP Addresses

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..forms.ipaddresses import AllocateIPsForm
from ..models import Notification
from ..views import LandingPageView


class IPAddressesView(LandingPageView):
    def __init__(self, request):
        super(IPAddressesView, self).__init__(request)
        self.initial_sort_key = 'public_ip'
        # self.items = self.get_items()  # Only need this when filters are displayed on the landing page
        self.prefix = '/ipaddresses'
        self.display_type = self.request.params.get('display', 'tableview')  # Set tableview as default
        self.conn = self.get_connection()

    def get_items(self):
        return self.conn.get_all_addresses() if self.conn else []

    @view_config(route_name='ipaddresses', renderer='../templates/ipaddresses/ipaddresses.pt')
    def ipaddresses_landing(self):
        json_items_endpoint = self.request.route_url('ipaddresses_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['domain', 'instance_id', 'public_ip']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='public_ip', name='IP Address'),
            dict(key='instance_id', name='Instance'),
        ]
        # Handle Allocate IP addresses form
        allocate_form = AllocateIPsForm(self.request, formdata=self.request.params)
        if self.request.method == 'POST':
            if allocate_form.validate():
                new_ips = []
                success_location = self.request.route_url('ipaddresses')
                ipcount = int(self.request.params.get('ipcount', 0))
                for i in xrange(ipcount):
                    new_ip = self.conn.allocate_address()
                    new_ips.append(new_ip.public_ip)
                notification_msg = u'Successfully allocated IPs {0}'.format(', '.join(new_ips))
                self.request.session.flash(notification_msg, queue=Notification.SUCCESS)
                return HTTPFound(location=success_location)

        return dict(
            display_type=self.display_type,
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            allocate_form=allocate_form,
        )

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
