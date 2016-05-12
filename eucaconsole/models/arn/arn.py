# -*- coding: utf-8 -*-
# Copyright 2016 Hewlett Packard Enterprise Development LP
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

class MetaARN(type):
    """Metaclass for AmazonResourceName subclasses.

    MetaARN provides a factory method for AmazonResourceName.  All classes that
    inherit from AmazonResourceName will be cataloged by the metaclass, so no
    further management of the factory method is necessary.
    """

    arn_types = []

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        mcs.arn_types.append(cls)
        return cls

    @classmethod
    def factory(mcs, arn):
        """AmazonResourceName factory method.

        Given an ARN string provided by AWS or Euca, return an instance of the
        appropriate AmazonResourceName subclass.

        instance = AmazonResourceName.factory(<arn>)
        """
        (_, partition, service, _) = arn.split(':', 3)
        for arn_type in mcs.arn_types:
            if arn_type.match(service):
                return arn_type(arn)


class ServiceNamespace(object):
    """AmazonResourceName service namespace class decorator.

    Decorates AmazonResourceName subclasses with the matching AWS service namespace.

    http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#genref-aws-service-namespaces
    """
    def __init__(self, arntype):
        self._arntype = arntype

    def __call__(self, cls):
        cls._arntype = self._arntype
        return cls


class AmazonResourceName(dict):
    """Parse an Amazon Resource Name string into its component parts.

    Not to be instantiated directly, use the AmazonResourceName.factory() method
    to return an object of the correct type.
    """
    __metaclass__ = MetaARN
    _arntype = None

    def __init__(self, arn=None):
        self.arn = None
        self.partition = None
        self.service = None
        self.region = None
        self.accountid = None

        if arn is not None:
            self.parse(arn)

    def __str__(self):
        pass

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    @classmethod
    def match(cls, service):
        """Match the ARN service namespace to the decorated ServiceNamespace."""
        return service == cls._arntype

    def parse(self, arn):
        (_, partition, service, region, accountid, resource) = arn.split(':', 5)

        self.arn = arn
        self.partition = partition
        self.service = service
        self.region = region
        self.accountid = accountid

        return resource
