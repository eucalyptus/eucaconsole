# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Pyramid views for Eucalyptus and AWS CloudFormation stacks

"""
import simplejson as json
import os
import urllib2

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..i18n import _
from ..forms import ChoicesManager, CFSampleTemplateManager

from ..forms.stacks import StacksDeleteForm, StacksFiltersForm, StacksCreateForm
from ..models import Notification
from ..models.auth import User
from ..views import LandingPageView, BaseView, JSONResponse
from . import boto_error_handler


class StacksView(LandingPageView):
    def __init__(self, request):
        super(StacksView, self).__init__(request)
        self.request = request
        self.cloudformation_conn = self.get_connection(conn_type="cloudformation")
        self.initial_sort_key = 'name'
        self.prefix = '/stacks'
        self.filter_keys = ['name', 'create-time']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.get_json_endpoint('stacks_json')
        self.delete_form = StacksDeleteForm(self.request, formdata=self.request.params or None)
        self.filters_form = StacksFiltersForm(
            self.request, cloud_type=self.cloud_type, formdata=self.request.params or None)
        search_facets = self.filters_form.facets
        self.render_dict = dict(
            filter_fields=False,
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='stacks', renderer='../templates/stacks/stacks.pt')
    def stacks_landing(self):
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @view_config(route_name='stacks_delete', request_method='POST')
    def stacks_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('stacks')
            prefix = _(u'Unable to delete stack')
            template = u'{0} {1} - {2}'.format(prefix, name, '{0}')
            with boto_error_handler(self.request, location, template):
                self.cloudformation_conn.delete_stack(name)
                prefix = _(u'Successfully deleted stack.')
                msg = u'{0} {1}'.format(prefix, name)
                queue = Notification.SUCCESS
                notification_msg = msg
                self.request.session.flash(notification_msg, queue=queue)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    @staticmethod
    def get_sort_keys():
        return [
            dict(key='name', name=_(u'Name: A to Z')),
            dict(key='-name', name=_(u'Name: Z to A')),
            dict(key='creation_time', name=_(u'Creation time: Oldest to Newest')),
            dict(key='-creation_time', name=_(u'Creation time: Newest to Oldest')),
        ]


class StacksJsonView(LandingPageView):
    """JSON response view for Stack landing page"""
    def __init__(self, request):
        super(StacksJsonView, self).__init__(request)
        self.cloudformation_conn = self.get_connection(conn_type="cloudformation")
        with boto_error_handler(request):
            self.items = self.get_items()

    @view_config(route_name='stacks_json', renderer='json', request_method='POST')
    def stacks_json(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        transitional_states = ['CREATE_IN_PROGRESS', 'ROLLBACK_IN_PROGRESS', 'DELETE_IN_PROGRESS']
        with boto_error_handler(self.request):
            stacks_array = []
            for stack in self.filter_items(self.items):
                is_transitional = stack.stack_status in transitional_states
                name = stack.stack_name
                status = stack.stack_status
                stacks_array.append(dict(
                    creation_time=self.dt_isoformat(stack.creation_time),
                    status=status.lower().capitalize().replace('_', '-'),
                    description=stack.description,
                    name=name,
                    transitional=is_transitional,
                ))
            return dict(results=stacks_array)

    def get_items(self):
        return self.cloudformation_conn.describe_stacks() if self.cloudformation_conn else []


class StackView(BaseView):
    """Views for single stack"""
    TEMPLATE = '../templates/stacks/stack_view.pt'

    def __init__(self, request):
        super(StackView, self).__init__(request)
        self.cloudformation_conn = self.get_connection(conn_type='cloudformation')
        with boto_error_handler(request):
            self.stack = self.get_stack()
        self.delete_form = StacksDeleteForm(self.request, formdata=self.request.params or None)
        search_facets = [
            {'name': 'status', 'label': _(u"Status"), 'options': [
                {'key': 'create-complete', 'label': _("Create Complete")},
                {'key': 'create-in-progress', 'label': _("Create In Progresss")},
                {'key': 'create-failed', 'label': _("Create Failed")},
                {'key': 'delete-complete', 'label': _("Delete Complete")},
                {'key': 'delete-in-progress', 'label': _("Delete In Progresss")},
                {'key': 'delete-failed', 'label': _("Delete Failed")},
                {'key': 'rollback-complete', 'label': _("Rollback Complete")},
                {'key': 'rollback-in-progress', 'label': _("Rollback In Progresss")},
                {'key': 'rollback-failed', 'label': _("Rollback Failed")}
            ]}
        ]
        self.render_dict = dict(
            stack=self.stack,
            stack_name=self.stack.stack_name if self.stack else '',
            stack_description=self.stack.description if self.stack else '',
            stack_id=self.stack.stack_id if self.stack else '',
            stack_creation_time=self.dt_isoformat(self.stack.creation_time),
            status=self.stack.stack_status.lower().capitalize().replace('_', '-'),
            delete_form=self.delete_form,
            in_use=False,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            filter_keys=[],
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='stack_view', renderer=TEMPLATE)
    def stack_view(self):
        return self.render_dict

    @view_config(route_name='stack_delete', request_method='POST', renderer=TEMPLATE)
    def stack_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            location = self.request.route_path('stacks')
            prefix = _(u'Unable to delete stack')
            template = u'{0} {1} - {2}'.format(prefix, self.stack.stack_name, '{0}')
            with boto_error_handler(self.request, location, template):
                msg = _(u"Deleting stack")
                self.log_request(u"{0} {1}".format(msg, name))
                self.cloudformation_conn.delete_stack(name)
                prefix = _(u'Successfully deleted stack.')
                msg = u'{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_stack(self):
        if self.cloudformation_conn:
            stack_param = self.request.matchdict.get('name')
            stacks = self.cloudformation_conn.describe_stacks(stack_name_or_id=stack_param)
            return stacks[0] if stacks else None
        return None

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'stack_name': self.stack.stack_name,
            'stack_status_json_url': self.request.route_path('stack_state_json', name=self.stack.stack_name),
            'stack_template_url': self.request.route_path('stack_template', name=self.stack.stack_name),
            'stack_events_url': self.request.route_path('stack_events', name=self.stack.stack_name),
            'stack_status': self.stack.stack_status.lower().capitalize().replace('_', '-'),
        }))


class StackStateView(BaseView):
    def __init__(self, request):
        super(StackStateView, self).__init__(request)
        self.request = request
        self.cloudformation_conn = self.get_connection(conn_type='cloudformation')
        self.stack_name = self.request.matchdict.get('name')

    @view_config(route_name='stack_state_json', renderer='json', request_method='GET')
    def stack_state_json(self):
        """Return current stack status"""
        with boto_error_handler(self.request):
            stacks = self.cloudformation_conn.describe_stacks(self.stack_name)
            stack = stacks[0] if stacks else None
            stack_resources = self.cloudformation_conn.list_stack_resources(self.stack_name)
            stack_status = stack.stack_status if stack else 'delete_complete'
            stack_outputs = stack.outputs if stack else None
            outputs = []
            for output in stack_outputs:
                outputs.append({'key': output.key, 'value': output.value})
            resources = []
            for resource in stack_resources:
                resources.append({
                    'type': resource.resource_type,
                    'logical_id': resource.logical_resource_id,
                    'physical_id': resource.physical_resource_id,
                    'status': resource.resource_status.lower().capitalize().replace('_', '-'),
                    'url': self.get_url_for_resource(resource.resource_type, resource.physical_resource_id),
                    'updated_timestamp': resource.LastUpdatedTimestamp})
            return dict(
                results=dict(
                    stack_status=stack_status.lower().capitalize().replace('_', '-'),
                    outputs=outputs,
                    resources=resources
                )
            )

    @view_config(route_name='stack_template', renderer='json', request_method='GET')
    def stack_template(self):
        """Return stack template"""
        with boto_error_handler(self.request):
            template = self.cloudformation_conn.get_template(self.stack_name)
            parsed = json.loads(template['GetTemplateResponse']['GetTemplateResult']['TemplateBody'])
            params = []
            for name in parsed['Parameters'].keys():
                param = parsed['Parameters'][name]
                params.append({'name': name, 'description': param['Description'], 'type': param['Type']})
            return dict(
                results=dict(description=parsed['Description'],
                             parameters=params)
            )

    @view_config(route_name='stack_events', renderer='json', request_method='GET')
    def stack_events(self):
        """Return stack events"""
        status = self.request.params.getall('status')
        with boto_error_handler(self.request):
            stack_events = self.cloudformation_conn.describe_stack_events(self.stack_name)
            events = []
            for event in stack_events:
                stack_status = event.resource_status.lower().replace('_', '-')

                if len(status) == 0 or stack_status in status:
                    events.append({
                        'timestamp': event.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'status': event.resource_status.lower().capitalize().replace('_', '-'),
                        'status_reason': event.resource_status_reason,
                        'type': event.resource_type,
                        'logical_id': event.logical_resource_id,
                        'physical_id': event.physical_resource_id,
                        'url': self.get_url_for_resource(event.resource_type, event.physical_resource_id)
                    })
            return dict(
                results=dict(events=events)
            )

    def get_url_for_resource(self, res_type, resource_id):
        url = None
        if res_type == "AWS::ElasticLoadBalancing::LoadBalancer":
            url = self.request.route_path('elb_view', id=resource_id)
        elif "AWS::EC2::" in res_type:
            if "SecurityGroup" in res_type:
                url = self.request.route_path('securitygroup_view', id=resource_id)
            elif "EIP" in res_type:
                url = self.request.route_path('ipaddress_view', id=resource_id)
            elif "Instance" in res_type:
                url = self.request.route_path('instance_view', id=resource_id)
            elif "Volume" in res_type:
                url = self.request.route_path('volume_view', id=resource_id)
        elif "AWS::AutoScaling::" in res_type:
            if "LaunchConfiguration" in res_type:
                url = self.request.route_path('launchconfig_view', id=resource_id)
            if "ScalingGroup" in res_type:
                url = self.request.route_path('scalinggroup_view', id=resource_id)
        elif "AWS::IAM::" in res_type:
            if "Group" in res_type:
                url = self.request.route_path('group_view', id=resource_id)
            elif "Role" in res_type:
                url = self.request.route_path('role_view', id=resource_id)
            elif "User" in res_type:
                url = self.request.route_path('user_view', id=resource_id)
        elif "AWS::S3::" in res_type:
            if "Bucket" in res_type:
                url = self.request.route_path('bucket_contents', id=resource_id)
        return url


class StackWizardView(BaseView):
    """View for Create Stack wizard"""
    TEMPLATE = '../templates/stacks/stack_wizard.pt'

    def __init__(self, request):
        super(StackWizardView, self).__init__(request)
        self.request = request
        self.create_form = None
        with boto_error_handler(self.request):
            s3_bucket = self.get_template_samples_bucket()
            self.create_form = StacksCreateForm(request, s3_bucket)
        self.render_dict = dict(
            create_form=self.create_form,
            controller_options_json=self.get_controller_options_json(),
        )

    def get_template_samples_bucket(self):
        sample_bucket = self.request.registry.settings.get('cloudformation.samples.bucket')
        if sample_bucket is None:
            return None
        s3_conn = self.get_connection(conn_type="s3")
        return s3_conn.get_bucket(sample_bucket)

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'stack_template_url': self.request.route_path('stack_template_parse'),
            'sample_templates': self.create_form.sample_template.choices
        }))

    @view_config(route_name='stack_new', renderer=TEMPLATE, request_method='GET')
    def stack_new(self):
        """Displays the Stack wizard"""
        return self.render_dict

    @view_config(route_name='stack_template_parse', renderer='json', request_method='POST')
    def stack_template_parse(self):
        """
        Fetches then parsed template to return information needed by wizard,
        namely description and parameters.
        """
        (template_url, parsed) = self.parse_store_template()
        params = []
        for name in parsed['Parameters'].keys():
            param = parsed['Parameters'][name]
            param_vals = {
                'name': name,
                'description': param['Description'] if 'Description' in param else '',
                'type': param['Type']
            }
            if 'Default' in param:
                param_vals['default'] = param['Default']
            if 'MinLength' in param:
                param_vals['min'] = param['MinLength']
            if 'MaxLength' in param:
                param_vals['max'] = param['MaxLength']
            if 'AllowedPattern' in param:
                param_vals['regex'] = param['AllowedPattern']
            if 'ConstraintDescription' in param:
                param_vals['constraint'] = param['ConstraintDescription']
            if 'AllowedValues' in param:
                param_vals['options'] = [(val, val) for val in param['AllowedValues']]
            # guess at more options
            if 'key' in name.lower():
                param_vals['options'] = self.get_key_options()  # fetch keypair names
            if 'image' in name.lower():
                param_vals['options'] = self.get_image_options()  # fetch image ids
            if 'kernel' in name.lower():
                param_vals['options'] = self.get_image_options(img_type='kernel')  # fetch kernel ids
            if 'ramdisk' in name.lower():
                param_vals['options'] = self.get_image_options(img_type='ramdisk')  # fetch ramdisk ids
            if 'cert' in name.lower():
                param_vals['options'] = self.get_cert_options()  # fetch server cert names
            if 'instance' in name.lower() and 'profile' in name.lower():
                param_vals['options'] = self.get_instance_profile_options()
            if ('vmtype' in name.lower() or 'instancetype' in name.lower()) and 'options' not in param_vals.keys():
                param_vals['options'] = self.get_vmtype_options()
            params.append(param_vals)
        return dict(
            results=dict(
                description=parsed['Description'] if 'Description' in parsed else '',
                parameters=params
            )
        )

#                parameters=BaseView.escape_json(json.dumps(params))
    def get_key_options(self):
        conn = self.get_connection()
        keys = conn.get_all_key_pairs()
        ret = []
        for key in keys:
            ret.append((key.name, key.name))
        return ret

    def get_image_options(self, img_type='machine'):
        conn = self.get_connection()
        region = self.request.session.get('region')
        images = []
        if img_type == 'machine':
            images = self.get_images(conn, [], [], region)
        elif img_type == 'kernel':
            images = conn.get_all_kernels()
        elif img_type == 'ramdisk':
            images = conn.get_all_ramdisks()
        ret = []
        for image in images:
            ret.append((image.id, image.name))
        return ret

    def get_cert_options(self):
        ret = []
        if self.cloud_type == 'euca':
            conn = self.get_connection(conn_type="iam")
            certs = conn.list_server_certs()
            certs = certs['list_server_certificates_response'][
                'list_server_certificates_result']['server_certificate_metadata_list']
            for cert in certs:
                ret.append((cert.arn, cert.server_certificate_name))
        return ret

    def get_instance_profile_options(self):
        ret = []
        if self.cloud_type == 'euca':
            conn = self.get_connection(conn_type="iam")
            profiles = conn.list_instance_profiles()
            profiles = profiles['list_instance_profiles_response'][
                'list_instance_profiles_result']['instance_profiles']
            for profile in profiles:
                ret.append((profile.arn, profile.instance_profile_name))
        return ret

    def get_vmtype_options(self):
        conn = self.get_connection()
        vmtypes = ChoicesManager(conn).instance_types(self.cloud_type)
        return vmtypes

    @view_config(route_name='stack_create', renderer=TEMPLATE, request_method='POST')
    def stack_create(self):
        if True:  # self.create_form.validate():
            stack_name = self.request.params.get('name')
            location = self.request.route_path('stacks')
            (template_url, parsed) = self.parse_store_template()
            params = []
            for name in parsed['Parameters'].keys():
                val = self.request.params.get(name)
                if val:
                    params.append((name, val))
            tags_json = self.request.params.get('tags')
            tags = None
            if tags_json:
                tags = json.loads(tags_json)
            with boto_error_handler(self.request, location):
                cloudformation_conn = self.get_connection(conn_type='cloudformation')
                self.log_request(u"Creating stack:{0}".format(stack_name))
                cloudformation_conn.create_stack(
                    stack_name, template_url=template_url,
                    parameters=params, tags=tags
                )
                msg = _(u'Successfully sent create stack request. '
                        u'It may take a moment to create the stack.')
                queue = Notification.SUCCESS
                self.request.session.flash(msg, queue=queue)
                location = self.request.route_path('stack_view', name=stack_name)
                return HTTPFound(location=location)
        else:
            self.request.error_messages = self.create_form.get_errors_list()
        return self.render_dict

    def parse_store_template(self):
        template_name = self.request.params.get('sample-template')
        template_url = self.request.params.get('template-url')
        files = self.request.POST.getall('template-file')
        template_body = ''

        if len(files) > 0 and len(str(files[0])) > 0:  # read from file
            # TODO: body limit is 51,200 in the API, check that!
            template_body = files[0].file.read()
            template_name = files[0].name
        elif template_url:  # read from url
            template_body = urllib2.urlopen(template_url).read()
            template_name = template_url[template_url.rindex('/') + 1:]
        else:
            s3_bucket = self.get_template_samples_bucket()
            mgr = CFSampleTemplateManager(s3_bucket)
            templates = mgr.get_template_list()
            for directory, files in templates:
                if template_name in [f for (name, f) in files]:
                    if directory == 's3':
                        s3_key = s3_bucket.get_key(template_name)
                        template_body = s3_key.get_contents_as_string()
                    else:
                        fd = open(os.path.join(directory, template_name), 'r')
                        template_body = fd.read()

        # now that we have it, store in S3
        s3_conn = self.get_connection(conn_type="s3")
        account_id = User.get_account_id(ec2_conn=self.get_connection(), request=self.request)
        region = self.request.session.get('region')
        bucket = s3_conn.create_bucket("cf-template-{acct}-{region}".format(acct=account_id, region=region))
        key = bucket.get_key(template_name)
        if key is None:
            key = bucket.new_key(template_name)
        key.set_contents_from_string(template_body)
        template_url = key.generate_url(300)  # 5 minute URL, more than enough time, right?

        parsed = json.loads(template_body)
        return template_url, parsed
