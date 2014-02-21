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
        self.target_type = self.request.params.get('type', 'user')  # 'user' or 'group'
        self.target_name = self.request.params.get('id', '')  # user or group name
        self.render_dict = dict(
            page_title=self.get_page_title(),
            create_form=self.create_form,
            policy_json_endpoint=self.policy_json_endpoint,
            policy_actions=permissions.POLICY_ACTIONS,
            controller_options=json.dumps(self.get_controller_options()),
            resource_choices=dict(
                instances=self.get_instance_choices(),
                images=self.get_image_choices(),
                volumes=self.get_volume_choices(),
                snapshots=self.get_snapshot_choices(),
                security_groups=self.get_security_group_choices(),
                key_pairs=self.get_key_pair_choices(),
            ),
        )

    @view_config(route_name='iam_policy_new', renderer=TEMPLATE, request_method='GET')
    def iam_policy_new(self):
        """Displays the Create IAM Policy wizard"""
        return self.render_dict

    @view_config(route_name='iam_policy_create', renderer=TEMPLATE, request_method='POST')
    def iam_policy_create(self):
        """Handles the POST from the Create IAM Policy wizard"""
        target_route = '{0}_view'.format(self.target_type)  # 'user_view' or 'group_view'
        location = self.request.route_url(target_route, name=self.target_name)  # redirect to detail page after submit
        if self.create_form.validate():
            policy_name = self.request.params.get('name')
            policy_json = self.request.params.get('policy', '{}')
            try:
                if self.target_type == 'user':
                    caller = self.iam_conn.put_user_policy
                else:
                    caller = self.iam_conn.put_group_policy
                caller(self.target_name, policy_name, policy_json)
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

    def get_page_title(self):
        prefix = _(u'Add access policy for')
        return '{0} {1} {2}'.format(prefix, self.target_type.capitalize(), self.target_name)

    def get_controller_options(self):
        return {
            'policyJsonEndpoint': self.policy_json_endpoint,
            'cloudType': self.cloud_type,
        }

    def get_instance_choices(self):
        choices = [('', _(u'All instances...'))]
        for instance in self.ec2_conn.get_only_instances():
            arn_prefix = self.get_arn_prefix('instance')
            value = '{0}{1}'.format(arn_prefix, instance.id)
            label = TaggedItemView.get_display_name(instance)
            choices.append((value, label))
        return choices

    def get_image_choices(self):
        choices = [('', _(u'All images...'))]
        # Set owner alias to 'self' for AWS
        owner_alias = 'self' if self.cloud_type == 'aws' else None
        owners = [owner_alias] if owner_alias else []
        images = self.ec2_conn.get_all_images(owners=owners, filters={'image-type': 'machine'})
        for image in images:
            arn_prefix = self.get_arn_prefix('image')
            value = '{0}{1}'.format(arn_prefix, image.id)
            label = TaggedItemView.get_display_name(image)
            choices.append((value, label))
        return choices

    def get_volume_choices(self):
        choices = [('', _(u'All volumes...'))]
        for volume in self.ec2_conn.get_all_volumes():
            arn_prefix = self.get_arn_prefix('volume')
            value = '{0}{1}'.format(arn_prefix, volume.id)
            label = TaggedItemView.get_display_name(volume)
            choices.append((value, label))
        return choices

    def get_snapshot_choices(self):
        choices = [('', _(u'All snapshots...'))]
        for snapshot in self.ec2_conn.get_all_snapshots():
            arn_prefix = self.get_arn_prefix('snapshot')
            value = '{0}{1}'.format(arn_prefix, snapshot.id)
            label = TaggedItemView.get_display_name(snapshot)
            choices.append((value, label))
        return choices

    def get_security_group_choices(self):
        choices = [('', _(u'All security groups...'))]
        for security_group in self.ec2_conn.get_all_security_groups():
            arn_prefix = self.get_arn_prefix('security-group')
            value = '{0}{1}'.format(arn_prefix, security_group.name)
            label = '{0} ({1})'.format(security_group.name, security_group.id)
            choices.append((value, label))
        return choices

    def get_key_pair_choices(self):
        choices = [('', _(u'All key pairs...'))]
        for key_pair in self.ec2_conn.get_all_key_pairs():
            arn_prefix = self.get_arn_prefix('key-pair')
            value = '{0}{1}'.format(arn_prefix, key_pair.name)
            label = key_pair.name
            choices.append((value, label))
        return choices

    def get_arn_prefix(self, resource):
        region = '*'
        if self.cloud_type == 'aws':
            region = self.region
        return 'arn:aws:ec2:{region}:*:{resource}/'.format(region=region, resource=resource)


class IAMPolicyWizardJsonView(BaseView):
    """View for returning JSON of canned policies"""

    @view_config(route_name='iam_policy_json', renderer='json', request_method='GET')
    def iam_policy_json(self):
        policy_type = self.request.params.get('type')
        policy_dict = policies.TYPE_POLICY_MAPPING.get(policy_type)
        if policy_dict:
            return dict(policy=policy_dict)
        return JSONResponse(status=404, message=_(u'Unable to locate policy'))


