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
Tests for Pyramid Layout-based panels

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from collections import namedtuple


import simplejson as json

from pyramid import testing

from eucaconsole.forms.securitygroups import SecurityGroupForm
from eucaconsole.views.panels import (
    form_field_row, image_picker, securitygroup_rules, tag_editor, autoscale_tag_editor, bdmapping_editor,
    s3_sharing_panel
)

from tests import BaseViewTestCase


class ImagePickerTests(BaseViewTestCase):
    request = testing.DummyRequest()
    request.session = dict(cloud_type='euca')

    def test_image_picker_panel(self):
        """Test the image picker panel"""
        panel = image_picker(None, self.request)
        controller_options = json.loads(panel.get('controller_options_json'))
        self.assertEqual(controller_options.get('images_json_endpoint'), self.request.route_path('images_json'))
        self.assertEqual(controller_options.get('cloud_type'), 'euca')


class TagEditorTests(BaseViewTestCase):
    request = testing.DummyRequest()

    def test_tag_editor_panel(self):
        """Test the standard tag editor panel"""
        tags = {'tag1key': 'tag1val', 'tag2key': 'tag2val'}
        panel = tag_editor(None, self.request, tags=tags, show_name_tag=False)
        controller_options = json.loads(panel.get('controller_options_json'))
        self.assertEqual(controller_options.get('tags'), tags)
        self.assertFalse(controller_options.get('show_name_tag'))

    def test_autoscale_tag_editor_panel(self):
        """Test the autoscaling tag editor panel"""
        Tag = namedtuple('Tag', ['key', 'value', 'propagate_at_launch'])
        tags = [
            Tag(key='foo', value='bar', propagate_at_launch=True),
        ]
        tags_output = [
            dict(name='foo', value='bar', propagate_at_launch=True),
        ]
        panel = autoscale_tag_editor(None, self.request, tags=tags)
        controller_options = json.loads(panel.get('controller_options_json'))
        self.assertEqual(controller_options.get('tags_list'), tags_output)


class SecurityGroupPanelsTestCase(BaseViewTestCase):
    form_class = SecurityGroupForm
    request = testing.DummyRequest()
    security_group = None
    form = form_class(request)

    def test_panel_readonly_html_attr(self):
        """Test if we set the proper HTML attr when passing a 'readonly' kwarg to the form_field_row panel"""
        fieldrow = form_field_row(None, self.request, self.form.description, readonly='readonly')
        self.assertTrue('readonly' in fieldrow.get('html_attrs').keys())

    def test_add_form(self):
        """Form field data should be empty if new item (i.e. security_group is None)"""
        self.assertTrue(self.form.name.data is None)
        self.assertTrue(self.form.description.data is None)

    def test_rules_editor_panel(self):
        """Test the security group rules editor panel"""
        Rule = namedtuple('Rule', ['ip_protocol', 'from_port', 'to_port', 'grants'])
        Grant = namedtuple('Grant', ['name', 'owner_id', 'group_id', 'cidr_ip'])
        rules = [
            Rule(ip_protocol='tcp', from_port=80, to_port=80,
                 grants=[Grant(name=None, owner_id='12345678', group_id=None, cidr_ip='127.0.0.1/32')])
        ]
        ruleseditor = securitygroup_rules(None, self.request, rules=rules)
        rules_output = [{
            'to_port': 80,
            'grants': [{'owner_id': '12345678', 'group_id': None, 'cidr_ip': '127.0.0.1/32', 'name': None}],
            'ip_protocol': 'tcp',
            'from_port': 80
        }]
        controller_options = json.loads(ruleseditor.get('controller_options_json'))
        self.assertEqual(controller_options.get('rules_array'), rules_output)
        self.assertTrue(ruleseditor.get('icmp_choices') is not None)


class BlockDeviceMappingEditorTests(BaseViewTestCase):
    request = testing.DummyRequest()
    Image = namedtuple('Image', ['block_device_mapping', 'root_device_name'])
    Device = namedtuple('Device', ['ephemeral_name', 'snapshot_id', 'size', 'delete_on_termination'])

    def test_bdm_editor_panel(self):
        """Test the block device mapping panel"""
        bdm_device = self.Device(snapshot_id='123456', size=1, delete_on_termination=True, ephemeral_name='foo')
        bdm = {'/dev/sda': bdm_device}
        image = self.Image(block_device_mapping=bdm, root_device_name='/dev/sda')
        panel = bdmapping_editor(None, self.request, image=image)
        controller_options = json.loads(panel.get('controller_options_json'))
        bdm_device = controller_options.get('bd_mapping').get('/dev/sda')
        self.assertEqual(bdm_device.get('snapshot_id'), '123456')
        self.assertEqual(bdm_device.get('size'), 1)
        self.assertTrue(bdm_device.get('delete_on_termination'))


class S3SharingPanelTests(BaseViewTestCase):
    request = testing.DummyRequest()

    def test_sharing_panel_for_create_bucket(self):
        panel = s3_sharing_panel(None, self.request, bucket_object=None)
        controller_options = json.loads(panel.get('controller_options_json'))
        self.assertEqual(controller_options.get('grants'), [])
