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
#
# This file may incorporate work covered under the following copyright
# and permission notice:
#
#   Copyright (c) 2012, Konsta Vesterinen
#
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * The names of the contributors may not be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#   WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT,
#   INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#   BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
#   OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Base classes for all tests

See http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html

"""
import collections
import unittest

from pyramid import testing
from wtforms import Field
from wtforms.validators import DataRequired, InputRequired, Length, Email, Optional, NumberRange

from eucaconsole.routes import urls
from eucaconsole.caches import short_term
from eucaconsole.caches import default_term
from eucaconsole.caches import long_term
from eucaconsole.caches import extra_long_term


class BaseViewTestCase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        for route in urls:
            self.config.add_route(route.name, route.pattern)

    def tearDown(self):
        testing.tearDown()


class BaseTestCase(unittest.TestCase):
    """Use this as a base when you need to run test with no routes automatically configured.
       Note: You probably want to use BaseViewTestCase instead."""
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

class BaseFormTestCase(unittest.TestCase):
    """Base form class, modified from wtforms-test to better work with CSRF forms.
       See https://github.com/kvesteri/wtforms-test/blob/master/wtforms_test/__init__.py
    """
    form_class = None
    request = None
    csrf_enabled = True

    def setUp(self):
        self.config = testing.setUp()
        memory_cache = 'dogpile.cache.memory'
        memory_cache_url = '127.0.0.1:11211'
        username = None
        password = None
        short_term.configure(
            memory_cache,
            expiration_time = 60,
            arguments = {
                'url':[memory_cache_url],
                'binary':True,
                'min_compress_len':1024,
                'behaviors':{"tcp_nodelay": True,"ketama":True},
                'username':username,
                'password':password
            },
        )
        default_term.configure(
            memory_cache,
            expiration_time = 300,
            arguments = {
                'url':[memory_cache_url],
                'binary':True,
                'min_compress_len':1024,
                'behaviors':{"tcp_nodelay": True,"ketama":True},
                'username':username,
                'password':password
            },
        )
        long_term.configure(
            memory_cache,
            expiration_time = 3600,
            arguments = {
                'url':[memory_cache_url],
                'binary':True,
                'min_compress_len':1024,
                'behaviors':{"tcp_nodelay": True,"ketama":True},
                'username':username,
                'password':password
            },
        )
        extra_long_term.configure(
            memory_cache,
            expiration_time = 43200,
            arguments = {
                'url':[memory_cache_url],
                'binary':True,
                'min_compress_len':1024,
                'behaviors':{"tcp_nodelay": True,"ketama":True},
                'username':username,
                'password':password
            },
        )

    def _make_form(self, csrf_enabled=False, *args, **kwargs):
        return self.form_class(request=self.request, csrf_enabled=self.csrf_enabled, *args, **kwargs)

    def _get_field(self, field_name):
        form = self._make_form()
        return getattr(form, field_name)

    def _get_validator(self, field, validator_class):
        for validator in field.validators:
            if isinstance(validator, validator_class):
                return validator

    def get_validator(self, field_name, validator_class):
        return self._get_validator(
            self._get_field(field_name),
            validator_class
        )

    def has_field(self, field_name):
        form = self._make_form()
        return hasattr(form, field_name)

    def assert_type(self, field_name, field_type):
        self.assert_has(field_name)
        assert self._get_field(field_name).__class__ is field_type

    def assert_has(self, field_name):
        try:
            field = self._get_field(field_name)
        except AttributeError:
            field = None
        msg = "Form does not have a field called '%s'." % field_name
        assert isinstance(field, Field), msg

    def assert_min(self, field_name, min_value):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple NumberRange validators
            if isinstance(validator, NumberRange):
                if validator.min == min_value:
                    found = True
        assert found, "Field does not have min value of %d" % min_value

    def assert_max(self, field_name, max_value):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple NumberRange validators
            if isinstance(validator, NumberRange):
                if validator.max == max_value:
                    found = True
        assert found, "Field does not have max value of %d" % max_value

    def assert_min_length(self, field_name, min_length):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple Length validators
            if isinstance(validator, Length):
                if validator.min == min_length:
                    found = True
        assert found, "Field does not have min length of %d" % min_length

    def assert_max_length(self, field_name, max_length):
        field = self._get_field(field_name)
        found = False
        for validator in field.validators:
            # we might have multiple Length validators
            if isinstance(validator, Length):
                if validator.max == max_length:
                    found = True
        assert found, "Field does not have max length of %d" % max_length

    def assert_description(self, field_name, description):
        field = self._get_field(field_name)
        assert field.description == description

    def assert_default(self, field_name, default):
        field = self._get_field(field_name)
        assert field.default == default

    def assert_label(self, field_name, label):
        field = self._get_field(field_name)
        assert field.label.text == label

    def assert_has_validator(self, field_name, validator):
        field = self._get_field(field_name)
        msg = "Field '%s' does not have validator %r." % (
            field_name, validator
        )
        assert self._get_validator(field, validator), msg

    def assert_not_optional(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is optional." % field_name
        assert not self._get_validator(field, DataRequired), msg

    def assert_optional(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is not optional." % field_name
        assert self._get_validator(field, Optional), msg

    def assert_choices(self, field_name, choices):
        field = self._get_field(field_name)
        assert field.choices == choices

    def assert_choice_values(self, field_name, choices):
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        field = self._get_field(field_name)
        assert compare(field.choices, choices)

    def assert_not_required(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is required." % field_name
        valid = self._get_validator(field, InputRequired) or self._get_validator(field, DataRequired)
        assert not valid, msg

    def assert_required(self, field_name):
        field = self._get_field(field_name)
        msg = "Field '%s' is not required." % field_name
        required = self._get_validator(field, InputRequired) or self._get_validator(field, DataRequired)
        assert required, msg

    def assert_email(self, field_name):
        field = self._get_field(field_name)
        msg = (
            "Field '%s' is not required to be a valid email address." %
            field_name
        )
        assert self._get_validator(field, Email), msg
