# -*- coding: utf-8 -*-
"""
Pyramid views for Eucalyptus and AWS key pairs

"""
import simplejson as json

from boto.exception import EC2ResponseError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config
from pyramid.response import Response

from ..forms.keypairs import KeyPairForm, KeyPairImportForm, KeyPairDeleteForm
from ..models import Notification
from ..views import BaseView, LandingPageView


class KeyPairsView(LandingPageView):
    def __init__(self, request):
        super(KeyPairsView, self).__init__(request)
        self.initial_sort_key = 'name'
        self.prefix = '/keypairs'
        self.delete_form = KeyPairDeleteForm(self.request, formdata=self.request.params or None)

    @view_config(route_name='keypairs', renderer='../templates/keypairs/keypairs.pt')
    def keypairs_landing(self):
        json_items_endpoint = self.request.route_url('keypairs_json')
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['name', 'fingerprint']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='name', name=_(u'Name')),
            dict(key='fingerprint', name=_(u'Fingerprint')),
        ]

        return dict(
            filter_fields=self.filter_fields,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            delete_form=self.delete_form,
        )


class KeyPairsJsonView(BaseView):
    def __init__(self, request):
        super(KeyPairsJsonView, self).__init__(request)
        self.conn = self.get_connection()

    @view_config(route_name='keypairs_json', renderer='json', request_method='GET')
    def keypairs_json(self):
        keypairs = []
        for keypair in self.get_items():
            keypairs.append(dict(
                name=keypair.name,
                fingerprint=keypair.fingerprint,
            ))
        return dict(results=keypairs)

    def get_items(self):
        return self.conn.get_all_key_pairs() if self.conn else []


class KeyPairView(BaseView):
    """Views for single Key Pair"""
    TEMPLATE = '../templates/keypairs/keypair_view.pt'

    def __init__(self, request):
        super(KeyPairView, self).__init__(request)
        self.conn = self.get_connection()
        self.keypair = self.get_keypair()
        self.keypair_route_id = self.request.matchdict.get('id')
        self.keypair_form = KeyPairForm(self.request, keypair=self.keypair, formdata=self.request.params or None)
        self.keypair_import_form = KeyPairImportForm(self.request, keypair=self.keypair, formdata=self.request.params or None)
        self.delete_form = KeyPairDeleteForm(self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            keypair=self.keypair,
            keypair_route_id=self.keypair_route_id,
            keypair_form=self.keypair_form,
            keypair_import_form=self.keypair_import_form,
            delete_form=self.delete_form,
            keypair_names=self.get_keypair_names(),
        )

    def get_keypair(self):
        keypair_param = self.request.matchdict.get('id')
        keypairs_param = [keypair_param]
        keypairs = self.conn.get_all_key_pairs(keynames=keypairs_param)
        keypair = keypairs[0] if keypairs else None
        return keypair 

    @view_config(route_name='keypair_view', renderer=TEMPLATE)
    def keypair_view(self):
        session = self.request.session
        new_keypair_created = False
        # Check if the session contains the new keypair material information
        if 'new_keypair_name' in session and session['new_keypair_name'] is not '':
            new_keypair_created = True

        self.render_dict['keypair_created'] = new_keypair_created
        return self.render_dict

    def get_keypair_names(self):
        keypairs = []
        if self.conn:
            keypairs = [k.name for k in self.conn.get_all_key_pairs()]
        return sorted(set(keypairs))

    @view_config(route_name='keypair_download', request_method='POST', renderer=TEMPLATE)
    def keypair_download(self):
        session = self.request.session
        if session.get('new_keypair_name'):
            name = session['new_keypair_name']
            material = session['material']
            # Clean the session information regrading the new keypair
            del session['new_keypair_name']
            del session['material']
            response = Response(content_type='application/x-pem-file;charset=ISO-8859-1')
            response.body = str(material)
            response.content_disposition='attachment; filename="{name}.pem"'.format(name=name)
            return response

        return self.render_dict

    @view_config(route_name='keypair_create', request_method='POST', renderer=TEMPLATE)
    def keypair_create(self):
        if self.keypair_form.validate():
            name = self.request.params.get('name')
            session = self.request.session
            new_keypair = None
            try:
                new_keypair = self.conn.create_key_pair(name)
                # Store the new keypair material information in the session
                session['new_keypair_name'] = new_keypair.name 
                session['material'] = new_keypair.material
                msg_template = _(u'Successfully created key pair {keypair}')
                msg = msg_template.format(keypair=name)
                queue = Notification.SUCCESS
                status = 200
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
                status = getattr(err, 'status', 400)
            if self.request.is_xhr:
                keypair_material = new_keypair.material if new_keypair else None
                resp_body = json.dumps(dict(message=msg, payload=keypair_material))
                return Response(status=status, body=resp_body, content_type='application/x-pem-file;charset=ISO-8859-1')
            else:
                location = self.request.route_url('keypair_view', id=name)
                self.request.session.flash(msg, queue=queue)
                return HTTPFound(location=location)
        if self.request.is_xhr:
            form_errors = ', '.join(self.keypair_form.get_errors_list())
            Response(status=400, resp_body=dict(message=form_errors))  # Validation failure = bad request
        else:
            self.request.error_messages = self.keypair_form.get_errors_list()
            return self.render_dict

    @view_config(route_name='keypair_import', request_method='POST', renderer=TEMPLATE)
    def keypair_import(self):
        if self.keypair_form.validate():
            name = self.request.params.get('name')
            key_material = self.request.params.get('key_material')
            msg = ""
            material = ""
            try:
                new_keypair = self.conn.import_key_pair(name, key_material)
                material = new_keypair.material
                msg_template = _(u'Successfully imported key pair {keypair}')
                msg = msg_template.format(keypair=name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            location = self.request.route_url('keypair_view', id=name)
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='keypair_delete', request_method='POST', renderer=TEMPLATE)
    def keypair_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            try:
                self.conn.delete_key_pair(name)
                prefix = _(u'Successfully deleted keypair')
                msg = '{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
            except EC2ResponseError as err:
                msg = err.message
                queue = Notification.ERROR
            notification_msg = msg
            self.request.session.flash(notification_msg, queue=queue)
            location = self.request.route_url('keypairs')
            return HTTPFound(location=location)

        return self.render_dict


