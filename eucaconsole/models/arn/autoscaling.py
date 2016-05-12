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

from arn import AmazonResourceName, ServiceNamespace


@ServiceNamespace('autoscaling')
class AutoScaling(AmazonResourceName):
    """AmazonResourceName for AutoScaling namespace."""

    def __init__(self, arn=None):
        self.resource_type = None
        self.autoscaling_group_name = None
        self.policy_name = None
        self.policy_id = None
        self.group_id = None

        super(AutoScaling, self).__init__(arn)

    def parse(self, arn):
        resource = super(AutoScaling, self).parse(arn)
        (resource_type, id, names) = resource.split(':', 2)

        self.resource_type = resource_type
        names_dict = dict(pair.split('/') for pair in names.split(':'))
        self.autoscaling_group_name = names_dict.get('autoScalingGroupName')
        self.policy_name = names_dict.get('policyName')

        if resource_type == 'scalingPolicy':
            self.policy_id = id
        else:
            self.group_id = id
