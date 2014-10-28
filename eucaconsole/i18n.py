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
i18n config

"""
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('eucaconsole')

LOCALES = ('en', 'de', 'el', 'es', 'fr', 'it', 'ru', 'zh_HANS', 'zh_HANT')


@subscriber(NewRequest)
def set_accepted_languages_locale(event):
    if not event.request.accept_language:
        return
    accepted = event.request.accept_language
    event.request._LOCALE_ = accepted.best_match(LOCALES, 'en')


def custom_locale_negotiator(request):
    """
    Determine the locale from the request object, a URL param, cookies, or the browser's Accept-Language header
    Fall back to pyramid.default_local_name setting
    """
    name = '_LOCALE_'
    locale_name = getattr(request, name, None) or request.params.get(name) or request.cookies.get(name)
    if locale_name is None:
        default_locale = request.registry.settings.get('pyramid.default_locale_name', 'en')
        locale_name = request.accept_language.best_match(LOCALES, default_locale)
        if not request.accept_language:
            locale_name = default_locale
    return locale_name

