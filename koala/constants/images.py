# -*- coding: utf-8 -*-
"""
Constants for Images

"""
from collections import namedtuple

from pyramid.i18n import TranslationString as _


Choice = namedtuple('Choice', ['key', 'pattern', 'name'])

# Platform choices for an Image (used to determine platform from the image description)
PLATFORM_CHOICES = [
    Choice('rhel5', r'(rhel|redhat).5', 'Red Hat 5'),
    Choice('rhel6', r'(rhel|redhat).6', 'Red Hat 6'),
    Choice('rhel', r'(rhel|redhat)', 'Red Hat'),
    Choice('centos5', r'centos.5', 'CentOS 5'),
    Choice('centos6', r'centos.6', 'CentOS 6'),
    Choice('centos', r'centos', 'CentOS'),
    Choice('lucid', r'(lucid|ubuntu.10[\W\s]04)', 'Ubuntu Lucid (10.04)'),
    Choice('precise', r'(precise|ubuntu.12[\W\s]04)', 'Ubuntu Precise (12.04)'),
    Choice('ubuntu', r'ubuntu', 'Ubuntu'),
    Choice('debian', r'debian', 'Debian'),
    Choice('fedora',  r'fedora', 'Fedora'),
    Choice('opensuse',  r'opensuse', 'OpenSUSE'),
    Choice('suse',  r'suse', 'SUSE Linux'),
    Choice('gentoo',  r'gentoo', 'Gentoo'),
    Choice('linux',  r'linux', 'Linux'),
    Choice('windows', r'windows', 'Windows'),
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

