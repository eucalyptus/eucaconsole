# -*- coding: utf-8 -*-
# Copyright 2015-2016 Hewlett Packard Enterprise Development LP
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
A collection of reusable utility methods

"""
from string import Template

from lxml import etree


def is_ufshost_error(conn, cloud_type):
    """
    Returns true if ufshost setting is not resolvable externally

    :type conn: boto.connection.AWSAuthConnection
    :param conn: a connection object which we get host from

    :type cloud_type: string
    :param cloud_type: usually 'aws' or 'euca'
    """
    ufshost = conn.host if cloud_type == 'euca' else ''
    return (ufshost in ['localhost', '127.0.0.1'])


def validate_xml(xml, schema):
    """
    :param xml: XML to validate
    :type xml: str
    :param schema: RelaxNG schema as string
    :type schema: str
    :return: tuple of (True, None) if valid, else (False, exception)
    :rtype: tuple
    """
    xml_tree = etree.fromstring(xml)
    relaxng_schema = etree.fromstring(schema)
    relaxng = etree.RelaxNG(relaxng_schema)
    try:
        relaxng.assertValid(xml_tree)
        return True, None
    except etree.DocumentInvalid as err:
        return False, err


def remove_namespace(xml, root_elem='CORSConfiguration', namespace='http://s3.amazonaws.com/doc/2006-03-01/'):
    """
    :param xml: XML to remove namespace from
    :type xml: str
    :param root_elem: root element of XML doc
    :type root_elem: str
    :param namespace: Namespace to remove
    :type namespace: str
    :return: XML string with namespaces removed
    :rtype: str
    """
    xml_tree = etree.fromstring(xml)
    ns_template = Template('{$ns}$elem')
    ns_pattern = ns_template.substitute(ns=namespace, elem=root_elem)
    etree.strip_attributes(xml_tree, ns_pattern)
    etree.cleanup_namespaces(xml_tree)
    return etree.tostring(xml_tree, pretty_print=True)
