# -*- coding: utf-8 -*-
"""
Base Forms

IMPORTANT: All forms needing CSRF protection should inherit from BaseSecureForm

"""
from pyramid.i18n import TranslationString as _
from wtforms.ext.csrf import SecureForm

from ..constants.instances import AWS_INSTANCE_TYPE_CHOICES, EUCA_INSTANCE_TYPE_CHOICES


BLANK_CHOICE = ('', _(u'select...'))


class BaseSecureForm(SecureForm):
    def __init__(self, request, **kwargs):
        self.request = request
        super(BaseSecureForm, self).__init__(**kwargs)

    def generate_csrf_token(self, csrf_context):
        return self.request.session.get_csrf_token()


class ChoicesManager(object):
    """Container for form choices reused across the app"""

    def __init__(self, conn=None):
        self.conn = conn

    def availability_zones(self, add_blank=True):
        """Returns a list of availability zone choices"""
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        zones = self.conn.get_all_zones() if self.conn else []  # TODO: cache me
        for zone in zones:
            choices.append((zone.name, zone.name))
        return sorted(choices)

    @staticmethod
    def instance_types(cloud_type='euca', add_blank=True):
        """Get instance type (e.g. m1.small) choices
            cloud_type is either 'euca' or 'aws'
        """
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if cloud_type == 'euca':
            # TODO: Pull instance types using DescribeInstanceTypes
            choices.extend(EUCA_INSTANCE_TYPE_CHOICES)
        elif cloud_type == 'aws':
            choices.extend(AWS_INSTANCE_TYPE_CHOICES)
        return choices

    def security_groups(self, add_blank=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        security_groups = self.conn.get_all_security_groups() if self.conn else []
        for sgroup in security_groups:
            if sgroup.id:
                choices.append((sgroup.name, sgroup.name))
        if not security_groups:
            choices.append(('', 'default'))
        return sorted(set(choices))

    def keypairs(self, add_blank=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        keypairs = self.conn.get_all_key_pairs()
        for keypair in keypairs:
            choices.append((keypair.name, keypair.name))
        return sorted(set(choices))

    def kernels(self):
        """Get kernel id choices"""
        choices = [('', _(u'Use default from image'))]
        kernel_images = self.conn.get_all_kernels()  # TODO: cache me
        for image in kernel_images:
            if image.kernel_id:
                choices.append((image.kernel_id, image.kernel_id))
        return sorted(set(choices))

    def ramdisks(self):
        """Get ramdisk id choices"""
        choices = [('', _(u'Use default from image'))]
        ramdisk_images = self.conn.get_all_ramdisks()  # TODO: cache me
        for image in ramdisk_images:
            if image.ramdisk_id:
                choices.append((image.ramdisk_id, image.ramdisk_id))
        return sorted(set(choices))

