# -*- coding: utf-8 -*-
# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
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
import base64
import simplejson as json
import hashlib
import logging
import os
import fnmatch
import time
import urllib2
from urllib2 import HTTPError, URLError
from boto.exception import BotoServerError

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..i18n import _
from ..forms import ChoicesManager, CFSampleTemplateManager

from ..forms.stacks import StacksDeleteForm, StacksFiltersForm, StacksCreateForm 
from ..models import Notification
from ..models.auth import User
from ..views import LandingPageView, BaseView, TaggedItemView, JSONResponse, JSONError
from . import boto_error_handler
from .. import utils

TEMPLATE_BODY_LIMIT = 460800


class StackMixin(object):
    def get_stack(self):
        if self.cloudformation_conn:
            try:
                stack_param = self.request.matchdict.get('name')
                if not(stack_param):
                    stack_param = self.request.params.get('stack-name')
                if not(stack_param):
                    return None
                stacks = self.cloudformation_conn.describe_stacks(stack_name_or_id=stack_param)
                return stacks[0] if stacks else None
            except BotoServerError:
                pass
        return None

    def get_create_template_bucket(self, create=False):
        s3_conn = self.get_connection(conn_type="s3")
        account_id = User.get_account_id(ec2_conn=self.get_connection(), request=self.request)
        region = self.request.session.get('region')
        for suffix in ['', 'a', 'b', 'c']:
            d = hashlib.md5()
            d.update(account_id)
            d.update(suffix)
            md5 = d.digest()
            acct_hash = base64.b64encode(md5, '--')
            acct_hash = acct_hash[:acct_hash.find('=')]
            try:
                bucket_name = "cf-template-{acct_hash}-{region}".format(
                    acct_hash=acct_hash.lower(),
                    region=region
                )
                if create:
                    bucket = s3_conn.create_bucket(bucket_name)
                else:
                    bucket = s3_conn.get_bucket(bucket_name)
                return bucket
            except BotoServerError as err:
                if err.code != 'BucketAlreadyExists' and create:
                    BaseView.handle_error(err=err, request=self.request)
        raise JSONError(status=500, message=_(
            u'Cannot create S3 bucket to store your CloudFormation template due to namespace collision. '
            u'Please contact your cloud administrator.'
        ))

    def get_template_location(self, stack_id, default_name=None):
        bucket = None
        try:
            bucket = self.get_create_template_bucket(create=False)
        except:
            pass
        stack_id = stack_id[stack_id.rfind('/') + 1:]
        d = hashlib.md5()
        d.update(stack_id)
        md5 = d.digest()
        stack_hash = base64.b64encode(md5, '--').replace('=', '')
        ret = {'template_name': default_name}
        if bucket is not None:
            keys = list(bucket.list(prefix=stack_hash))
            if len(keys) > 0:
                key = keys[0].key
                name = key[key.rfind('-') + 1:]
                ret['template_bucket'] = bucket.name
                ret['template_key'] = key
                ret['template_name'] = name
        return ret


class StacksView(LandingPageView):
    def __init__(self, request):
        super(StacksView, self).__init__(request)
        self.title_parts = [_(u'Stacks')]
        self.cloudformation_conn = self.get_connection(conn_type="cloudformation")
        self.initial_sort_key = 'name'
        self.prefix = '/stacks'
        self.filter_keys = ['name', 'create-time']
        self.sort_keys = self.get_sort_keys()
        self.json_items_endpoint = self.get_json_endpoint('stacks_json')
        self.delete_form = StacksDeleteForm(request, formdata=request.params or None)
        self.filters_form = StacksFiltersForm(
            request, cloud_type=self.cloud_type, formdata=request.params or None)
        search_facets = self.filters_form.facets
        self.render_dict = dict(
            filter_keys=self.filter_keys,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=self.json_items_endpoint,
            delete_form=self.delete_form,
            delete_stack_url=request.route_path('stacks_delete'),
            update_stack_url=request.route_path('stack_update', name='_name_'),
            ufshost_error=utils.is_ufshost_error(self.cloudformation_conn, self.cloud_type)
        )

    @view_config(route_name='stacks', renderer='../templates/stacks/stacks.pt')
    def stacks_landing(self):
        # sort_keys are passed to sorting drop-down
        return self.render_dict

    @view_config(route_name='stacks_delete', request_method='POST', xhr=True)
    def stacks_delete(self):
        if self.delete_form.validate():
            name = self.request.params.get('name')
            prefix = _(u'Unable to delete stack')
            template = u'{0} {1} - {2}'.format(prefix, name, '{0}')
            with boto_error_handler(self.request, None, template):
                self.cloudformation_conn.delete_stack(name)
                prefix = _(u'Successfully sent delete stack request. It may take a moment to delete ')
                msg = u'{0} {1}'.format(prefix, name)
                return JSONResponse(status=200, message=msg)
        form_errors = ', '.join(self.delete_form.get_errors_list())
        return JSONResponse(status=400, message=form_errors)  # Validation failure = bad request

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
        transitional_states = [
            'CREATE_IN_PROGRESS',
            'ROLLBACK_IN_PROGRESS',
            'DELETE_IN_PROGRESS',
            'CREATE_FAILED',
            'UPDATE_IN_PROGRESS',
            'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
            'UPDATE_ROLLBACK_IN_PROGRESS',
            'UPDATE_ROLLBACK_FAILED',
            'UPDATE_ROLLBACK_COMPLETED_CLEANUP_IN_PROGRESS',
            'UPDATE_FAILED'
        ]
        with boto_error_handler(self.request):
            stacks_array = []
            for stack in self.filter_items(self.items):
                is_transitional = stack.stack_status in transitional_states
                name = stack.stack_name
                status = stack.stack_status
                if status == 'DELETE_COMPLETE':
                    continue
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


class StackView(BaseView, StackMixin):
    """Views for single stack"""
    TEMPLATE = '../templates/stacks/stack_view.pt'

    def __init__(self, request):
        super(StackView, self).__init__(request)
        self.title_parts = [_(u'Stack'), request.matchdict.get('name')]
        self.cloudformation_conn = self.get_connection(conn_type='cloudformation')
        with boto_error_handler(request):
            self.stack = self.get_stack()
        self.delete_form = StacksDeleteForm(self.request, formdata=self.request.params or None)
        search_facets = [
            {'name': 'status', 'label': _(u"Status"), 'options': [
                {'key': 'create-complete', 'label': _("Create Complete")},
                {'key': 'create-in-progress', 'label': _("Create In Progresss")},
                {'key': 'create-failed', 'label': _("Create Failed")},
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
            stack_creation_time=self.dt_isoformat(self.stack.creation_time) if self.stack else None,
            status=self.stack.stack_status.lower().capitalize().replace('_', '-') if self.stack else None,
            delete_form=self.delete_form,
            in_use=False,
            search_facets=BaseView.escape_json(json.dumps(search_facets)),
            filter_keys=[],
            controller_options_json=self.get_controller_options_json(),
        )

    @view_config(route_name='stack_view', request_method='GET', renderer=TEMPLATE)
    def stack_view(self):
        if self.stack is None and self.request.matchdict.get('name') != 'new':
            raise HTTPNotFound
        template_info = self.get_template_location(self.stack.stack_id)
        template_info.update(self.render_dict)
        return template_info

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
                prefix = _(u'Successfully sent delete stack request. It may take a moment to delete ')
                msg = u'{0} {1}'.format(prefix, name)
                self.request.session.flash(msg, queue=Notification.SUCCESS)
                time.sleep(1)  # delay to allow server to update state before moving user on
            return HTTPFound(location=location)
        else:
            self.request.error_messages = self.delete_form.get_errors_list()
        return self.render_dict

    def get_controller_options_json(self):
        if self.stack is None:
            return '{}'
        else:
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
                outputs.append({'key': output.key, 'description': output.description, 'value': output.value})
            resources = []
            for resource in stack_resources:
                resources.append({
                    'type': resource.resource_type,
                    'logical_id': resource.logical_resource_id,
                    'physical_id': resource.physical_resource_id,
                    'status': resource.resource_status.lower().capitalize().replace('_', '-'),
                    'url': StackStateView.get_url_for_resource(
                        self.request,
                        resource.resource_type,
                        resource.physical_resource_id
                    ),
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
            response = self.cloudformation_conn.get_template(self.stack_name)
            template = response['GetTemplateResponse']['GetTemplateResult']['TemplateBody']
            
            return dict(
                results=template
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
                        'status': stack_status,
                        'status_reason': event.resource_status_reason,
                        'type': event.resource_type,
                        'logical_id': event.logical_resource_id,
                        'physical_id': event.physical_resource_id,
                        'url': StackStateView.get_url_for_resource(
                            self.request,
                            event.resource_type,
                            event.physical_resource_id
                        )
                    })
            return dict(
                results=dict(events=events)
            )

    @staticmethod
    def get_url_for_resource(request, res_type, resource_id):
        url = None
        if res_type == "AWS::ElasticLoadBalancing::LoadBalancer":
            url = request.route_path('elb_view', id=resource_id)
        elif "AWS::EC2::" in res_type:
            if "SecurityGroup" in res_type:
                url = request.route_path('securitygroup_view', id=resource_id)
            elif res_type[10:] == "EIP":
                url = request.route_path('ipaddress_view', public_ip=resource_id)
            elif "Instance" in res_type:
                url = request.route_path('instance_view', id=resource_id)
            elif "Volume" in res_type:
                url = request.route_path('volume_view', id=resource_id)
        elif "AWS::AutoScaling::" in res_type:
            if "LaunchConfiguration" in res_type:
                url = request.route_path('launchconfig_view', id=resource_id)
            if "ScalingGroup" in res_type:
                url = request.route_path('scalinggroup_view', id=resource_id)
        elif "AWS::IAM::" in res_type:
            if "Group" in res_type:
                url = request.route_path('group_view', name=resource_id)
            elif "Role" in res_type:
                url = request.route_path('role_view', name=resource_id)
            elif "User" in res_type:
                url = request.route_path('user_view', name=resource_id)
        elif "AWS::S3::" in res_type:
            if "Bucket" in res_type:
                url = request.route_path('bucket_contents', name=resource_id, subpath='')
        elif res_type == "AWS::CloudWatch::Alarm":
            url = request.route_path('cloudwatch_alarm_view', alarm_id=base64.b64encode(bytes(resource_id), '--'))
        return url


class StackWizardView(BaseView, StackMixin):
    """View for Create Stack wizard"""
    TEMPLATE = '../templates/stacks/stack_wizard.pt'
    TEMPLATE_UPDATE = '../templates/stacks/stack_update.pt'

    def __init__(self, request):
        super(StackWizardView, self).__init__(request)
        self.cloudformation_conn = self.get_connection(conn_type='cloudformation')
        self.title_parts = [_(u'Stack'), _(u'Create')]
        self.create_form = None
        location = self.request.route_path('stacks')
        with boto_error_handler(self.request, location):
            s3_bucket = self.get_template_samples_bucket()
            self.create_form = StacksCreateForm(request, s3_bucket)
            self.stack = self.get_stack()
        self.render_dict = dict(
            create_form=self.create_form,
            controller_options_json=self.get_controller_options_json(),
        )

    def get_template_samples_bucket(self):
        sample_bucket = self.request.registry.settings.get('cloudformation.samples.bucket')
        if sample_bucket is None:
            return None
        s3_conn = self.get_connection(conn_type="s3")
        try:
            return s3_conn.get_bucket(sample_bucket)
        except BotoServerError:
            logging.warn(_(u'Configuration error: cloudformation.samples.bucket is referencing bucket that is not visible to this user.'))
            return None

    def get_controller_options_json(self):
        return BaseView.escape_json(json.dumps({
            'stack_template_url': self.request.route_path('stack_template_parse'),
            'convert_template_url': self.request.route_path('stack_template_convert'),
            'stack_template_read_url':
                self.request.route_path('stack_template', name=self.stack.stack_name) if self.stack else '',
            'sample_templates': self.create_form.sample_template.choices
        }))

    @view_config(route_name='stack_new', renderer=TEMPLATE, request_method='GET')
    def stack_new(self):
        """Displays the Stack wizard"""
        return self.render_dict

    @view_config(route_name='stack_update', renderer=TEMPLATE_UPDATE, request_method='GET')
    def stack_update_view(self):
        """Displays the Stack update wizard"""
        stack_name = self.request.matchdict.get('name')
        self.title_parts = [_(u'Stack'), stack_name, _(u'Update')]
        ret = dict(
            stack_name=stack_name,
        )
        template_info = self.get_template_location(self.stack.stack_id, default_name=_(u'Edit template'))
        ret.update(template_info)
        ret.update(self.render_dict)
        return ret

    @view_config(route_name='stack_update', renderer=TEMPLATE_UPDATE, request_method='POST')
    def stack_update(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        stack_name = self.request.matchdict.get('name')
        location = self.request.route_path('stack_update', name=stack_name)
        (template_url, template_name, parsed) = self.parse_store_template()
        capabilities = ['CAPABILITY_IAM']
        params = []
        if 'Parameters' in parsed.keys():
            for name in parsed['Parameters']:
                val = self.request.params.get(name)
                if val:
                    params.append((name, val))
        with boto_error_handler(self.request, location):
            self.log_request(u"Updating stack:{0}".format(stack_name))
            result = self.cloudformation_conn.update_stack(
                stack_name, template_url=template_url, capabilities=capabilities,
                parameters=params
            )
            stack_id = result[result.rfind('/') + 1:]
            d = hashlib.md5()
            d.update(stack_id)
            md5 = d.digest()
            stack_hash = base64.b64encode(md5, '--').replace('=', '')
            bucket = self.get_create_template_bucket(create=True)
            bucket.copy_key(
                new_key_name="{0}-{1}".format(stack_hash, template_name),
                src_key_name=template_name,
                src_bucket_name=bucket.name
            )
            bucket.delete_key(template_name)

            msg = _(u'Successfully sent update stack request. '
                    u'It may take a moment to update the stack.')
            queue = Notification.SUCCESS
            self.request.session.flash(msg, queue=queue)
            location = self.request.route_path('stack_view', name=stack_name)
            return HTTPFound(location=location)

    @view_config(route_name='stack_cancel_update', request_method='POST', xhr=True)
    def stack_cancel_update(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        stack_name = self.request.matchdict.get('name')
        with boto_error_handler(self.request):
            self.log_request(u"Cancelling update of stack:{0}".format(stack_name))
            self.cloudformation_conn.cancel_update_stack(stack_name)
            msg = _(u'Successfully sent cancel update request. '
                    u'It may take a moment to cancel the stack update.')
            return JSONResponse(status=200, message=msg)

    @view_config(route_name='stack_template_parse', renderer='json', request_method='POST')
    def stack_template_parse(self):
        """
        Fetches then parses template to return information needed by wizard,
        namely description and parameters.
        """
        with boto_error_handler(self.request):
            try:
                (template_url, template_name, parsed) = self.parse_store_template()
                if 'Resources' not in parsed:
                    raise JSONError(message=_(u'Invalid CloudFormation Template, Resources not found'), status=400)
                exception_list = []
                if self.request.params.get('inputtype') != 'sample' and \
                   self.request.session.get('cloud_type', 'euca') == 'euca':
                    exception_list = StackWizardView.identify_aws_template(parsed)
                if len(exception_list) > 0:
                    # massage for the browser
                    service_list = []
                    resource_list = []
                    property_list = []
                    parameter_list = []
                    for resource in exception_list:
                        if resource['type'] == 'Parameter':
                            parameter_list.append(resource['name'])
                        else:
                            tmp = resource['type']
                            tmp = tmp[5:]
                            if 'property' in resource.keys():
                                property_list.append('{0} ({1})'.format(tmp, resource['name']))
                            elif tmp.find('::') > -1:  # this means there's a resource there
                                resource_list.append(tmp)
                            else:
                                service_list.append(tmp)
                    service_list = list(set(service_list))
                    resource_list = list(set(resource_list))
                    property_list = list(set(property_list))
                    return dict(
                        results=dict(
                            template_key=template_name,
                            description=parsed['Description'] if 'Description' in parsed else '',
                            service_list=service_list,
                            resource_list=resource_list,
                            property_list=property_list,
                            parameter_list=parameter_list
                        )
                    )
                params = []
                if 'Parameters' in parsed.keys():
                    params = self.generate_param_list(parsed)
                    if self.stack:
                        # populate defaults with actual values from stack
                        for param in params:
                            result = [p.value for p in self.stack.parameters if p.key == param['name']]
                            if result:
                                param['default'] = result[0]
                return dict(
                    results=dict(
                        template_key=template_name,
                        description=parsed['Description'] if 'Description' in parsed else '',
                        parameters=params,
                        template_bucket=self.get_create_template_bucket().name
                    )
                )
            except ValueError as json_err:
                raise JSONError(message=_(u'Invalid JSON File ({0})').format(json_err.message), status=400)
            except HTTPError as http_err:
                raise JSONError(message=_(u"""
                    Cannot read URL ({0}) If this URL is for an S3 object, be sure 
                    that either the object has public read permissions or that the 
                    URL is signed with authentication information.
                 """).format(http_err.reason), status=400)

    @view_config(route_name='stack_template_convert', renderer='json', request_method='POST')
    def stack_template_convert(self):
        """
        Fetches then parsed template to return information needed by wizard,
        namely description and parameters.
        """
        with boto_error_handler(self.request):
            (template_url, template_name, parsed) = self.parse_store_template()
            StackWizardView.identify_aws_template(parsed, modify=True)
            template_body = json.dumps(parsed, indent=2)

            # now, store it back in S3
            bucket = self.get_create_template_bucket(create=True)
            key = bucket.get_key(template_name)
            if key is None:
                key = bucket.new_key(template_name)
            key.set_contents_from_string(template_body)

            params = []
            if 'Parameters' in parsed.keys():
                params = self.generate_param_list(parsed)
            return dict(
                results=dict(
                    template_key=template_name,
                    parameters=params
                )
            )

    @staticmethod
    def get_s3_template_url(key):
        template_url = key.generate_url(1)
        return template_url[:template_url.find('?')]

    def generate_param_list(self, parsed):
        """
        Valid values are [
            String,
            Number,
            CommaDelimitedList,
            AWS::EC2::AvailabilityZone::Name,
            AWS::EC2::Image::Id,
            AWS::EC2::Instance::Id,
            AWS::EC2::KeyPair::KeyName,
            AWS::EC2::SecurityGroup::GroupName,
            AWS::EC2::SecurityGroup::Id,
            AWS::EC2::Subnet::Id,
            AWS::EC2::Volume::Id,
            AWS::EC2::VPC::Id,
            List<String>,
            List<Number>,
            List<AWS::EC2::AvailabilityZone::Name>,
            List<AWS::EC2::Image::Id>,
            List<AWS::EC2::Instance::Id>,
            List<AWS::EC2::KeyPair::KeyName>,
            List<AWS::EC2::SecurityGroup::GroupName>,
            List<AWS::EC2::SecurityGroup::Id>,
            List<AWS::EC2::Subnet::Id>,
            List<AWS::EC2::Volume::Id>,
            List<AWS::EC2::VPC::Id>
        ]
        """
        params = []
        for name in parsed['Parameters']:
            param = parsed['Parameters'][name]
            param_type = param['Type']
            param_vals = {
                'name': name,
                'description': param['Description'] if 'Description' in param else '',
                'type': param_type
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
            name_l = name.lower()
            if 'key' in name_l or param_type == 'AWS::EC2::KeyPair::KeyName':
                param_vals['options'] = self.get_key_options()  # fetch keypair names
            if 'security' in name_l and 'group' in name_l or param_type == 'AWS::EC2::SecurityGroup::GroupName':
                param_vals['options'] = self.get_group_options()  # fetch security group names
            if 'kernel' in name_l:
                param_vals['options'] = self.get_image_options(img_type='kernel')  # fetch kernel ids
            if 'ramdisk' in name_l:
                param_vals['options'] = self.get_image_options(img_type='ramdisk')  # fetch ramdisk ids
            if 'cert' in name_l:
                param_vals['options'] = self.get_cert_options()  # fetch server cert names
            if 'instance' in name_l and 'profile' in name_l:
                param_vals['options'] = self.get_instance_profile_options()
            if ('instance' in name_l and 'instancetype' not in name_l) or param_type == 'AWS::EC2::Instance::Id':
                param_vals['options'] = self.get_instance_options()  # fetch instances
            if 'volume' in name_l or param_type == 'AWS::EC2::Volume::Id':
                param_vals['options'] = self.get_volume_options()  # fetch volumes
            if ('vmtype' in name_l or 'instancetype' in name_l) and \
                    'options' not in param_vals.keys():
                param_vals['options'] = self.get_vmtype_options()
            if 'zone' in name_l or param_type == 'AWS::EC2::AvailabilityZone::Name':
                param_vals['options'] = self.get_availability_zone_options()
            # if no default, and options are a single value, set that as default
            if 'default' not in param_vals.keys() and \
                    'options' in param_vals.keys() and len(param_vals['options']) == 1:
                param_vals['default'] = param_vals['options'][0][0]
            param_vals['chosen'] = True if \
                'options' in param_vals.keys() and len(param_vals['options']) > 9 \
                else False
            if 'image' in name_l or param_type == 'AWS::EC2::Image::Id':
                if self.request.session.get('cloud_type', 'euca') == 'aws':
                    # populate with amazon and user's images
                    param_vals['options'] = self.get_image_options(owner_alias='self')
                    param_vals['options'].extend(self.get_image_options(owner_alias='amazon'))
                else:
                    param_vals['options'] = self.get_image_options()  # fetch image ids
                # force image param to use chosen
                param_vals['chosen'] = True
            params.append(param_vals)
        return params

    def get_key_options(self):
        conn = self.get_connection()
        keys = conn.get_all_key_pairs()
        ret = []
        for key in keys:
            ret.append((key.name, key.name))
        return ret

    def get_group_options(self):
        conn = self.get_connection()
        groups = conn.get_all_security_groups()
        ret = []
        for group in groups:
            ret.append((group.name, group.name))
        return ret

    def get_instance_options(self):
        conn = self.get_connection()
        instances = conn.get_only_instances()
        ret = []
        for instance in instances:
            ret.append((instance.id, TaggedItemView.get_display_name(instance)))
        return ret

    def get_volume_options(self):
        conn = self.get_connection()
        volumes = conn.get_all_volumes()
        ret = []
        for volume in volumes:
            ret.append((volume.id, TaggedItemView.get_display_name(volume)))
        return ret

    def get_image_options(self, img_type='machine', owner_alias=None):
        conn = self.get_connection()
        region = self.request.session.get('region')
        owners = [owner_alias] if owner_alias else []
        images = []
        if img_type == 'machine':
            images = self.get_images(conn, owners, [], region)
        elif img_type == 'kernel':
            images = conn.get_all_kernels()
        elif img_type == 'ramdisk':
            images = conn.get_all_ramdisks()
        ret = []
        for image in images:
            ret.append((image.id, "{0} ({1})".format(image.name, image.id)))
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

    def get_availability_zone_options(self):
        conn = self.get_connection()
        zones = ChoicesManager(conn).availability_zones(self.cloud_type, add_blank=False)
        return zones

    @view_config(route_name='stack_create', renderer=TEMPLATE, request_method='POST')
    def stack_create(self):
        if True:  # self.create_form.validate():
            stack_name = self.request.params.get('name')
            location = self.request.route_path('stacks')
            (template_url, template_name, parsed) = self.parse_store_template()
            capabilities = ['CAPABILITY_IAM']
            params = []
            if 'Parameters' in parsed.keys():
                for name in parsed['Parameters']:
                    val = self.request.params.get(name)
                    if val:
                        params.append((name, val))
            tags_json = self.request.params.get('tags')
            tags = None
            if tags_json:
                tags = json.loads(tags_json)
            with boto_error_handler(self.request, location):
                self.log_request(u"Creating stack:{0}".format(stack_name))
                result = self.cloudformation_conn.create_stack(
                    stack_name, template_url=template_url, capabilities=capabilities,
                    parameters=params, tags=tags
                )
                stack_id = result[result.rfind('/') + 1:]
                d = hashlib.md5()
                d.update(stack_id)
                md5 = d.digest()
                stack_hash = base64.b64encode(md5, '--').replace('=', '')
                bucket = self.get_create_template_bucket(create=True)
                bucket.copy_key(
                    new_key_name="{0}-{1}".format(stack_hash, template_name),
                    src_key_name=template_name,
                    src_bucket_name=bucket.name
                )
                bucket.delete_key(template_name)

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
        s3_template_key = self.request.params.get('s3-template-key')
        if s3_template_key:
            # pull previously uploaded...
            bucket = self.get_create_template_bucket(create=True)
            key = bucket.get_key(s3_template_key)
            template_name = s3_template_key
            template_body = key.get_contents_as_string()
            template_url = self.get_s3_template_url(key)
        else:
            template_name = self.request.params.get('sample-template')
            template_url = self.request.params.get('template-url')
            files = self.request.POST.getall('template-file')
            template_body = self.request.params.get('template-body')

            if len(files) > 0 and len(str(files[0])) > 0:  # read from file
                files[0].file.seek(0, 2)  # seek to end
                if files[0].file.tell() > TEMPLATE_BODY_LIMIT:
                    raise JSONError(status=400, message=_(u'File too large: ') + files[0].filename)
                files[0].file.seek(0, 0)  # seek to start
                template_body = files[0].file.read()
                template_name = files[0].filename
            elif template_url:  # read from url
                whitelist = self.request.registry.settings.get('cloudformation.url.whitelist', 'http://*, https://*')
                match = False
                for pattern in whitelist.split(','):
                    matches = fnmatch.fnmatch(template_url, pattern.strip())
                    if matches:
                        match = True
                if not match:
                    msg = _(u'The URL is invalid. Valid URLs can only include ')
                    last_comma_idx = whitelist.rfind(',')
                    if last_comma_idx != -1:
                        whitelist = whitelist[:last_comma_idx] + _(u' or') + whitelist[last_comma_idx + 1:]
                    msg = msg + whitelist + _(u' Please change your URL.')
                    raise JSONError(
                        status=400,
                        message=msg
                    )
                try:
                    template_body = urllib2.urlopen(template_url).read(TEMPLATE_BODY_LIMIT)
                except URLError:
                    raise JSONError(status=400, message=_(u'Cannot read from url provided.'))
                template_name = template_url[template_url.rindex('/') + 1:]
                if len(template_body) > TEMPLATE_BODY_LIMIT:
                    raise JSONError(status=400, message=_(u'Template too large: ') + template_name)
            elif template_body:
                # just proceed if body provided with request
                template_name = 'current'
            elif template_name is None and self.stack:
                # loading template from existing stack
                template_name = 'current'
                response = self.cloudformation_conn.get_template(self.stack.stack_name)
                template_body = response['GetTemplateResponse']['GetTemplateResult']['TemplateBody']
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
            bucket = self.get_create_template_bucket(create=True)
            key = bucket.get_key(template_name)
            if key is None:
                key = bucket.new_key(template_name)
            key.set_contents_from_string(template_body)
            template_url = self.get_s3_template_url(key)

        parsed = json.loads(template_body)
        return template_url, template_name, parsed

    @staticmethod
    def identify_aws_template(parsed, modify=False):
        """
        drawn from here:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html
        and https://www.eucalyptus.com/docs/eucalyptus/4.1.1/index.html#cloudformation/cf_overview.html
        """
        aws_resource_prefixes = [
            'AWS::AutoScaling::LifecycleHook',
            'AWS::AutoScaling::ScheduledAction',
            'AWS::CloudFront',
            'AWS::CloudTrail',
            'AWS::DynamoDB',
            'AWS::EC2::VPCEndpoint',
            'AWS::EC2::VPCPeeringConnection',
            'AWS::EC2::VPNConnection',
            'AWS::EC2::VPNConnectionRoute',
            'AWS::EC2::VPNGateway',
            'AWS::EC2::VPNGatewayRoutePropagation',
            'AWS::ElastiCache',
            'AWS::ElasticBeanstalk',
            'AWS::Kinesis',
            'AWS::Logs',
            'AWS::OpsWOrks',
            'AWS::Redshift',
            'AWS::RDS',
            'AWS::Route53',
            'AWS::S3::BucketPolicy',
            'AWS::SDB',
            'AWS::SNS',
            'AWS::SQS'
        ]
        unsupported_properties = [
            {'resource': 'AWS::AutoScaling::AutoScalingGroup', 'properties': [
                'HealthCheckType', 'Tags', 'VpcZoneIdentifier'
            ]},
            {'resource': 'AWS::AutoScaling::LaunchConiguration', 'properties': [
                'AssociatePublicIpAddress'
            ]},
            {'resource': 'AWS::EC2::EIP', 'properties': [
                'Domain'
            ]},
            {'resource': 'AWS::EC2::Volume', 'properties': [
                'HealthCheckType', 'Tags'
            ]},
            {'resource': 'AWS::ElasticLoadBalancing::LoadBalancer', 'properties': [
                'AccessLoggingPolicy', 'ConnectionDrainingPolicy',
                'Policies.InstancePorts', 'Policies.LoadBalancerPorts'
            ]},
            {'resource': 'AWS::IAM::AccessKey', 'properties': [
                'Serial'
            ]}
        ]
        ret = []
        # first pass, find non-euca resources
        for name in parsed['Resources']:
            resource = parsed['Resources'][name]
            for prefix in aws_resource_prefixes:
                if resource['Type'].find(prefix) == 0:
                    ret.append({'name': name, 'type': prefix})

        # second pass, find non-euca properties
        for name in parsed['Resources']:
            resource = parsed['Resources'][name]
            for props in unsupported_properties:
                if resource['Type'].find(props['resource']) == 0:
                    for prop in props['properties']:
                        if 'Properties' in resource and prop in resource['Properties'].keys():
                            ret.append({
                                'name': prop,
                                'type': props['resource'],
                                'property': True
                            })

        # third pass, find refs to cloud-specific resources
        def find_image_ref(_name, item):
            if _name == 'Parameters':
                return  # ignore refs already in params
            if type(item) is dict and 'ImageId' in item.keys():
                img_item = item['ImageId']
                if isinstance(img_item, dict) and 'Ref' not in img_item.keys():
                    # check for emi lookup in map
                    if 'Fn::FindInMap' in img_item.keys():
                        map_name = img_item['Fn::FindInMap'][0]
                        if parsed['Mappings'] and parsed['Mappings'][map_name]:
                            img_map = parsed['Mappings'][map_name]
                            if json.dumps(img_map).find('emi-') > -1:
                                return
                    ret.append({
                        'name': 'ImageId',
                        'type': 'Parameter',
                        'item': item})
        StackWizardView.traverse(parsed, find_image_ref)

        if modify:
            for res in ret:
                # remove resources found in pass 1
                for name in parsed['Resources'].keys():
                    if res['name'] == name and 'property' not in res.keys():
                        del parsed['Resources'][name]
                # modify resource refs into params
                if res['name'] == 'ImageId':
                    res['item']['ImageId'] = {'Ref': 'ImageId'}
                    parsed['Parameters']['ImageId'] = dict(
                        Description='Image required to run this template',
                        Type='String'
                    )
            # and, because we provide instance types, remove 'AllowedValues' for InstanceType
            if 'Parameters' in parsed.keys():
                for name in parsed['Parameters']:
                    if name == 'InstanceType' and 'AllowedValues' in parsed['Parameters'][name]:
                        del parsed['Parameters'][name]['AllowedValues']

        return ret

    @staticmethod
    def traverse(graph, func, depth=0):
        if depth > 5:   # safety valve
            return
        if type(graph) is list:
            for item in graph:
                func(None, item)
                StackWizardView.traverse(item, func, depth + 1)
        if type(graph) is dict:
            for key in graph:
                item = graph[key]
                func(key, item)
                StackWizardView.traverse(item, func, depth + 1)
