# -*- coding: utf-8 -*-
# Copyright 2013-2016 Hewlett Packard Enterprise Development LP
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
Angular 1.4/1.5 Compatible WTForm Classes

"""

from wtforms import SelectField, SelectMultipleField


def clean_value(v):
    """Return value with Angular 1.4/1.5 prefix (e.g. 'string:') removed if str/unicode"""
    if isinstance(v, str) or isinstance(v, unicode):
        return v.replace('string:', '').strip()
    return v


class AngularCompatibleSelectField(SelectField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = self.coerce(clean_value(valuelist[0]))
            except ValueError:
                raise ValueError(self.gettext('Invalid Choice: could not coerce'))


class AngularCompatibleSelectMultipleField(SelectMultipleField):
    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(clean_value(x)) for x in valuelist)
        except ValueError:
            raise ValueError(self.gettext('Invalid choice(s): one or more data inputs could not be coerced'))
