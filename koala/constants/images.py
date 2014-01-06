# -*- coding: utf-8 -*-
"""
Constants for Images

"""
from collections import namedtuple

from pyramid.i18n import TranslationString as _


PlatformChoice = namedtuple('Choice', ['key', 'pattern', 'name'])

# Platform choices for an Image (used to determine platform from the image description)
PLATFORM_CHOICES = [
    PlatformChoice('redhat', r'(rhel|redhat).5', 'Red Hat 5'),
    PlatformChoice('redhat', r'(rhel|redhat).6', 'Red Hat 6'),
    PlatformChoice('redhat', r'(rhel|redhat)', 'Red Hat'),
    PlatformChoice('centos', r'centos.5', 'CentOS 5'),
    PlatformChoice('centos', r'centos.6', 'CentOS 6'),
    PlatformChoice('centos', r'centos', 'CentOS'),
    PlatformChoice('ubuntu', r'(lucid|ubuntu.10[\W\s]04)', 'Ubuntu Lucid (10.04)'),
    PlatformChoice('ubuntu', r'(precise|ubuntu.12[\W\s]04)', 'Ubuntu Precise (12.04)'),
    PlatformChoice('ubuntu', r'ubuntu', 'Ubuntu'),
    PlatformChoice('debian', r'debian', 'Debian'),
    PlatformChoice('fedora',  r'fedora', 'Fedora'),
    PlatformChoice('suse',  r'opensuse', 'OpenSUSE'),
    PlatformChoice('suse',  r'suse', 'SUSE Linux'),
    PlatformChoice('gentoo',  r'gentoo', 'Gentoo'),
    PlatformChoice('linux',  r'linux', 'Linux'),
    PlatformChoice('windows', r'windows', 'Windows'),
]


# Choices for Images Landing Page and Image Picker widget
OwnerChoice = namedtuple('OwnerChoice', ['key', 'label'])

EUCA_IMAGE_OWNER_ALIAS_CHOICES = (
    OwnerChoice(key='', label='Anyone'),
    OwnerChoice(key='self', label='Me')
)

AWS_IMAGE_OWNER_ALIAS_CHOICES = (
    OwnerChoice(key='self', label=_(u'Owned by me')),
    OwnerChoice(key='amazon', label=_(u'Amazon AMIs')),
    OwnerChoice(key='aws-marketplace', label=_(u'AWS Marketplace')),
)

