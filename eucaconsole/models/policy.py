# -*- coding: utf-8 -*-
# Copyright 2017 Ent. Services Development Corporation LP
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
Value objects for ELB Policies which boto 2 doesn't support for the Describe operation

"""

from boto.resultset import ResultSet

class PolicyAttributeDescription(object):
    def __init__(self, connection=None):
        self.attr_name = None
        self.attr_value = None

    def __repr__(self):
        return 'PolicyAttribute:%s=%s' % (self.attr_name, self.attr_value)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'AttributeName':
            self.attr_name = value
        elif name == 'AttributeValue':
            self.attr_value = value


class Policy(object):
    def __init__(self, connection=None):
        self.policy_name = None

    def __repr__(self):
        return 'Policy:%s' % self.policy_name

    def startElement(self, name, attrs, connection):
        if name == 'PolicyAttributeDescriptions':
            self.attrs = ResultSet([('member', PolicyAttributeDescription)])
            return self.attrs

    def endElement(self, name, value, connection):
        if name == 'PolicyName':
            self.policy_name = value
        
