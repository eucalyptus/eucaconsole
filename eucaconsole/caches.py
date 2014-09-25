# Copyright 2014 Eucalyptus Systems, Inc.
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


import inspect
import pylibmc
from hashlib import sha1
from dogpile.cache import make_region

def euca_key_generator(namespace, fn):
    if fn is None:
        has_self = True
    else:
        args = inspect.getargspec(fn)
        has_self = args[0] and args[0][0] in ('self', 'cls')
    def generate_key(*arg):
        # generate a key:
        # "namespace_arg1_arg2_arg3..."
        if has_self:
            arg = arg[1:]
        key = namespace + "|" + "_".join(map(str, arg))

        # return cache key
        # apply sha1 to obfuscate key contents
        #return sha1(key).hexdigest()
        return key

    return generate_key

def invalidate_cache(cache, namespace, *arg):
    key = euca_key_generator(namespace, None)(*arg)
    try:
        cache.delete(key)
    except pylibmc.Error as err:
        pass  # ignore memcached communication error... we tried

# caches available within the app
short_term = make_region(function_key_generator=euca_key_generator)
default_term = make_region(function_key_generator=euca_key_generator)
long_term = make_region(function_key_generator=euca_key_generator)
extra_long_term = make_region(function_key_generator=euca_key_generator)


