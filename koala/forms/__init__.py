# -*- coding: utf-8 -*-
"""
Base Forms

IMPORTANT: All forms needing CSRF protection should inherit from BaseSecureForm

"""
from pyramid.i18n import TranslationString as _
from wtforms.ext.csrf import SecureForm

from ..constants.instances import AWS_INSTANCE_TYPE_CHOICES
from boto.ec2.vmtype import VmType

BLANK_CHOICE = ('', _(u'select...'))


class BaseSecureForm(SecureForm):
    def __init__(self, request, **kwargs):
        self.request = request
        super(BaseSecureForm, self).__init__(**kwargs)

    def generate_csrf_token(self, csrf_context):
        return self.request.session.get_csrf_token()

    def get_errors_list(self):
        """Convenience method to get all form validation errors as a list of message strings"""
        error_messages = []
        for errors in self.errors.values():
            for error in errors:
                error_messages.append(error)
        return error_messages


class ChoicesManager(object):
    """Container for form choices reused across the app"""

    def __init__(self, conn=None):
        """"Note: conn param could be a connection object of any type, based on the choices required"""
        self.conn = conn

    #### EC2 connection type choices
    ##

    def availability_zones(self, zones=None, add_blank=True):
        """Returns a list of availability zone choices. Will fetch zones if not passed"""
        choices = []
        zones = zones or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if not zones and self.conn is not None:
            zones = self.conn.get_all_zones()
        for zone in zones:
            choices.append((zone.name, zone.name))
        return sorted(choices)

    def instance_types(self, cloud_type='euca', add_blank=True):
        """Get instance type (e.g. m1.small) choices
            cloud_type is either 'euca' or 'aws'
        """
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        if cloud_type == 'euca':
            if self.conn is not None:
                types = self.conn.get_list('DescribeInstanceTypes', {}, [('euca:item', VmType)], verb='POST')
                for vmtype in types:
                    vmtype_str = '{0}: {1} CPUs, {2} memory (MB), {3} disk (GB,root device)'.format(vmtype.name, vmtype.cores, vmtype.memory, vmtype.disk)
                    vmtype_tuple = vmtype.name, vmtype_str
                    choices.append(vmtype_tuple)
            else:
                choices.append(BLANK_CHOICE)
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

    def keypairs(self, keypairs=None, add_blank=True):
        choices = []
        if add_blank:
            choices.append(BLANK_CHOICE)
        keypairs = keypairs or []
        if not keypairs and self.conn is not None:
            keypairs = self.conn.get_all_key_pairs()
        for keypair in keypairs:
            choices.append((keypair.name, keypair.name))
        return sorted(set(choices))

    def elastic_ips(self, instance=None, ipaddresses=None, add_blank=True):
        choices = [('', _(u'None assigned'))]
        ipaddresses = ipaddresses or []
        if not ipaddresses and self.conn is not None:
            ipaddresses = self.conn.get_all_addresses()
        for eip in ipaddresses:
            choices.append((eip.public_ip, eip.public_ip))
        if instance and instance.ip_address:
            choices.append((instance.ip_address, instance.ip_address))
        return sorted(set(choices))

    def kernels(self, kernel_images=None, image=None):
        """Get kernel id choices"""
        choices = [('', _(u'Use default from image'))]
        kernel_images = kernel_images or []
        if not kernel_images and self.conn is not None:
            kernel_images = self.conn.get_all_kernels()  # TODO: cache me
        for kernel_image in kernel_images:
            if kernel_image.id:
                choices.append((kernel_image.id, kernel_image.id))
        if image:
            choices.append((image.kernel_id, image.kernel_id))
        return sorted(set(choices))

    def ramdisks(self, ramdisk_images=None, image=None):
        """Get ramdisk id choices"""
        choices = [('', _(u'Use default from image'))]
        ramdisk_images = ramdisk_images or []
        if not ramdisk_images and self.conn is not None:
            ramdisk_images = self.conn.get_all_ramdisks()  # TODO: cache me
        for ramdisk_image in ramdisk_images:
            if ramdisk_image.id:
                choices.append((ramdisk_image.id, ramdisk_image.id))
        if image:
            choices.append((image.ramdisk_id, image.ramdisk_id))
        return sorted(set(choices))

    #### AutoScale connection type choices
    ##

    def scaling_groups(self, scaling_groups=None, add_blank=True):
        """Returns a list of scaling group choices"""
        choices = []
        scaling_groups = scaling_groups or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        # Note: self.conn is an ELBConnection
        if not scaling_groups and self.conn is not None:
            scaling_groups = self.conn.get_all_groups()
        for scaling_group in scaling_groups:
            choices.append((scaling_group.name, scaling_group.name))
        return sorted(choices)

    #### ELB connection type choices
    ##

    def load_balancers(self, load_balancers=None, add_blank=True):
        """Returns a list of load balancer choices.  Will fetch load balancers if not passed"""
        choices = []
        load_balancers = load_balancers or []
        if add_blank:
            choices.append(BLANK_CHOICE)
        # Note: self.conn is an ELBConnection
        if not load_balancers and self.conn is not None:
            load_balancers = self.conn.get_all_load_balancers()
        for load_balancer in load_balancers:
            choices.append((load_balancer.name, load_balancer.name))
        return sorted(choices)
