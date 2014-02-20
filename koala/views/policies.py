# -*- coding: utf-8 -*-
"""
Pyramid views for IAM Policies (permissions)

"""
import simplejson as json

from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.view import view_config

from ..constants import policies, permissions
from ..forms.policies import IAMPolicyWizardForm
from ..models import Notification
from ..views import BaseView, JSONResponse, TaggedItemView


class IAMPolicyWizardView(BaseView):
    """Create IAM Policy wizard"""
    TEMPLATE = '../templates/policies/iam_policy_wizard.pt'

    def __init__(self, request):
        super(IAMPolicyWizardView, self).__init__(request)
        self.request = request
        self.ec2_conn = self.get_connection()
        self.iam_conn = self.get_connection(conn_type='iam')
        self.policy_json_endpoint = self.request.route_url('iam_policy_json')
        self.create_form = IAMPolicyWizardForm(request=self.request, formdata=self.request.params or None)
        self.render_dict = dict(
            create_form=self.create_form,
            policy_json_endpoint=self.policy_json_endpoint,
            policy_actions=permissions.POLICY_ACTIONS,
            controller_options=json.dumps(self.get_controller_options()),
            instance_choices=self.get_instance_choices(),
        )

    @view_config(route_name='iam_policy_new', renderer=TEMPLATE, request_method='GET')
    def iam_policy_new(self):
        """Displays the Create IAM Policy wizard"""
        return self.render_dict

    @view_config(route_name='iam_policy_create', renderer=TEMPLATE, request_method='POST')
    def iam_policy_create(self):
        """Handles the POST from the Create IAM Policy wizard"""
        target_type = self.request.params.get('type')  # 'user' or 'group'
        target_route = '{0}_view'.format(target_type)  # 'user_view' or 'group_view'
        target_name = self.request.params.get('id')  # user or group name
        location = self.request.route_url(target_route, name=target_name)  # redirect to detail page after submit
        if self.create_form.validate():
            policy_name = self.request.params.get('name')
            policy_json = self.request.params.get('policy', '{}')
            try:
                if target_type == 'user':
                    caller = self.iam_conn.put_user_policy
                else:
                    caller = self.iam_conn.put_group_policy
                caller(target_name, policy_name, policy_json)
                prefix = _(u'Successfully created IAM policy')
                msg = '{0} {1}'.format(prefix, policy_name)
                queue = Notification.SUCCESS
            except BotoServerError as err:
                msg = err.message
                queue = Notification.ERROR
            self.request.session.flash(msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    def get_controller_options(self):
        return {
            'policyJsonEndpoint': self.policy_json_endpoint,
        }

    def get_instance_choices(self):
        choices = [('', _(u'All instances...'))]
        for instance in self.ec2_conn.get_only_instances():
            cloud_type = self.request.session.get('cloud_type', 'euca')
            region = '*'
            if cloud_type == 'aws':
                default_region = self.request.registry.settings.get('aws.default.region')
                region = self.request.session.get('region', default_region)
            instance_arn_prefix = 'arn:aws:ec2:{0}:*:instance/'.format(region)
            value = '{0}{1}'.format(instance_arn_prefix, instance.id)
            label = TaggedItemView.get_display_name(instance)
            choices.append((value, label))
        return choices


class IAMPolicyWizardJsonView(BaseView):
    """View for returning JSON of canned policies"""

    @view_config(route_name='iam_policy_json', renderer='json', request_method='GET')
    def iam_policy_json(self):
        policy_type = self.request.params.get('type')
        policy_dict = policies.TYPE_POLICY_MAPPING.get(policy_type)
        if policy_dict:
            return dict(policy=policy_dict)
        return JSONResponse(status=404, message=_(u'Unable to locate policy'))


