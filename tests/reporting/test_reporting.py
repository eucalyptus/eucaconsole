# Copyright 2013-2017 Ent. Services Development Corporation LP
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
Reporting tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
import unittest
import simplejson as json

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from tests import BaseViewTestCase

from eucaconsole.views.reporting import ReportingAPIView

class ReportingAPIViewTests(unittest.TestCase):
    policy_doc = '{ \
      "Version": "2011-04-01", \
      "Statement": [ \
        { \
          "Action": "s3:GetBucketAcl", \
          "Resource": "arn:aws:s3:::testbucket/*", \
          "Effect": "Allow", \
          "Principal": { \
            "AWS": "arn:aws:iam::012345678901:root" \
          } \
        } \
      ] \
    }'

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_update_policy_doc(self):
        policy = ReportingAPIView.update_bucket_policy(self.policy_doc, '012345678901', 'testbucket')
        policy = json.loads(policy)
        stmt = policy['Statement']
        self.assertEquals(len(stmt), 3)
        action = policy['Statement'][2]['Action'][0]
        self.assertEquals(action, 's3:PutObject')
        principal = policy['Statement'][2]['Principal']['AWS']
        self.assertEquals(principal, 'arn:aws:iam::012345678901:root')
        resource = policy['Statement'][2]['Resource']
        self.assertEquals(resource, 'arn:aws:s3:::testbucket/*')
        self.assertEquals(principal, 'arn:aws:iam::012345678901:root')

