# -*- coding: utf-8 -*-
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
Pyramid configuration tests

"""
from pyramid.paster import get_appsettings
from pyramid.settings import asbool

from tests import BaseTestCase

SETTINGS = get_appsettings('conf/console.ini', name='main')


class CacheImagesSettingTestCase(BaseTestCase):

    def test_images_cache_is_disabled_by_default(self):
        cache_setting = SETTINGS.get('cache.images.disable')
        self.assertEqual(asbool(cache_setting), True)


class GovCloudSettingTestCase(BaseTestCase):

    def test_govcloud_setting_is_available_and_false_by_default(self):
        govcloud_setting = SETTINGS.get('aws.govcloud.enabled')
        self.assertEqual(asbool(govcloud_setting), False)


class NonConfigurableSettingsTestCase(BaseTestCase):

    def test_pyramid_includes_setting_is_not_in_default_config(self):
        setting = SETTINGS.get('pyramid.includes')
        self.assertEqual(setting, None)

    def test_session_type_setting_is_not_in_default_config(self):
        setting = SETTINGS.get('session.type')
        self.assertEqual(setting, None)

    def test_session_httponly_setting_is_not_in_default_config(self):
        setting = SETTINGS.get('session.httponly')
        self.assertEqual(setting, None)

    def test_cache_memory_setting_is_not_in_default_config(self):
        setting = SETTINGS.get('cache.memory')
        self.assertEqual(setting, None)
