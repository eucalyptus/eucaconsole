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
Quotas tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from eucaconsole.forms import BaseSecureForm
from eucaconsole.forms.quotas import QuotasForm

from tests import BaseViewTestCase, BaseFormTestCase


class QuotasUpdateFormTestCase(BaseFormTestCase):
    """Quotas form used on user detail and new user pages"""
    form_class = QuotasForm
    request = testing.DummyRequest()
    form = form_class(request)
    policy_doc = '{ \
      "Version": "2011-04-01", \
      "Statement": [ \
        { \
          "Action": "s3:CreateBucket", \
          "Resource": "*", \
          "Effect": "Limit", \
          "Condition": { \
            "NumericLessThanEquals": { \
              "s3:quota-bucketnumber": "1" \
            } \
          } \
        }, \
        { \
          "Action": "elasticloadbalancing:createloadbalancer", \
          "Resource": "*", \
          "Effect": "Limit", \
          "Condition": { \
            "NumericLessThanEquals": { \
              "elasticloadbalancing:quota-loadbalancernumber": "2" \
            } \
          } \
        } \
      ] \
    }'

    def test_secure_form(self):
        self.has_field('csrf_token')
        self.assertTrue(issubclass(self.form_class, BaseSecureForm))

    def test_policy_parsing(self):
        self.form.scan_policy(self.policy_doc)
        self.assertEquals(self.form.s3_buckets_max.data, "1")
        self.assertEquals(self.form.elb_load_balancers_max.data, "2")
