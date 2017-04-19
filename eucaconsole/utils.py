# -*- coding: utf-8 -*-
# Copyright 2015-2017 Ent. Services Development Corporation LP
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
import re

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
    return ufshost in ['localhost', '127.0.0.1']


def validate_xml(xml, schema):
    """
    Validate XML string against a RelaxNG schema
    :param xml: XML to validate
    :type xml: str
    :param schema: RelaxNG schema as string
    :type schema: str
    :return: tuple of (True, None) if valid, else (False, exception)
    :rtype: tuple
    """
    # Ensure XML document is well-formed
    try:
        xml_tree = etree.fromstring(xml.strip())
    except etree.XMLSyntaxError as err:
        return False, err

    # Now validate against schema
    relaxng_schema = etree.fromstring(schema)
    relaxng = etree.RelaxNG(relaxng_schema)

    try:
        relaxng.assertValid(xml_tree)
        return True, None
    except etree.DocumentInvalid as err:
        return False, err


def remove_namespace(xml, count=1):
    """
    Remove namespaces from XML root element
    :param xml: XML to remove namespaces from
    :type xml: str
    :param count: Limit namespace removal to ___ items
    :type count: int
    :return: XML string with namespace removed
    :rtype: str
    """
    return re.sub(' xmlns="[^"]+"', '', xml, count=count)
