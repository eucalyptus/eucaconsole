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
Main WSGI app

The WSGI app object returned from main() is invoked from the following section in the console.ini config file...

[app:main]
use = egg:eucaconsole

...which points to eucaconsole.egg-info/entry_points.txt
[paste.app_factory]
main = eucaconsole:main

"""
from hashlib import sha1
from dogpile.cache import make_region

from .config import get_configurator

def euca_key_generator(namespace, fn):
    def generate_key(*arg):
        print str(arg)
        # generate a key:
        # "namespace_arg1_arg2_arg3..."
        key = namespace + "_" + \
                          "_".join(str(s) for s in arg[1:])

        # store key template
        #user_keys.add(key_template)

        # return cache key
        print "cache key : "+key
        # apply sha1 to obfuscate key contents
        #return sha1(key).hexdigest()
        return key

    return generate_key

def invalidate_cache(cache, namespace, *arg):
    key = euca_key_generator(namespace, None)(*arg)
    print "$$$$$$$  invalidating cache key : "+key
    cache.delete(key)

# caches available within the app
short_term = make_region(function_key_generator=euca_key_generator)
default_term = make_region(function_key_generator=euca_key_generator)
long_term = make_region(function_key_generator=euca_key_generator)
extra_long_term = make_region(function_key_generator=euca_key_generator)


def main(global_config, **settings):
    """Return a Pyramid WSGI application"""
    app_config = get_configurator(settings)
    return app_config.make_wsgi_app()
