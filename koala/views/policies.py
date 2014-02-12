# -*- coding: utf-8 -*-
"""
Pyramid views for IAM Policies (permissions)

"""
from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..constants import policies
from ..forms.policies import IAMPolicyWizardForm
from ..models import Notification
from ..views import BaseView, JSONResponse


class IAMPolicyWizardView(BaseView):
    """Create IAM Policy wizard"""
    TEMPLATE = '../templates/policies/iam_policy_wizard.pt'

    def __init__(self, request):
        super(IAMPolicyWizardView, self).__init__(request)
        self.request = request
        self.conn = self.get_connection(conn_type='iam')
        self.policy_json_endpoint = self.request.route_url('iam_policy_json')
        self.create_form = IAMPolicyWizardForm(request=self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            create_form=self.create_form,
            policy_json_endpoint=self.policy_json_endpoint,
        )

    @view_config(route_name='iam_policy_new', renderer=TEMPLATE, request_method='GET')
    def iam_policy_new(self):
        """Displays the Create IAM Policy wizard"""
        return self.render_dict

    @view_config(route_name='iam_policy_create', renderer=TEMPLATE, request_method='POST')
    def iam_policy_create(self):
        """Handles the POST from the Create IAM Policy wizard"""
        location = self.request.route_url('users')
        if self.create_form.validate():
            name = self.request.params.get('name')
            try:
                # self.conn.put_user_policy()
                msg = _(u'Successfully created IAM policy.')
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        return self.render_dict


class IAMPolicyWizardJsonView(BaseView):
    """View for returning JSON of canned policies"""

    @view_config(route_name='iam_policy_json', renderer='json', request_method='GET')
    def iam_policy_json(self):
        policy_type = self.request.params.get('type')
        policy_dict = policies.TYPE_POLICY_MAPPING.get(policy_type)
        if policy_dict:
            return dict(policy=policy_dict)
        return JSONResponse(status=404, message=_(u'Unable to locate policy'))


