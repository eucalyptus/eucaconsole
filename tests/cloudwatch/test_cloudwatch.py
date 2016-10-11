# -*- coding: utf-8 -*-
# Copyright 2013-2015 Hewlett Packard Enterprise Development LP
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
Tests for CloudWatch

"""
from eucaconsole.views.cloudwatchapi import CloudWatchAPIMixin

from tests import BaseTestCase


class CloudWatchAPITestCase(BaseTestCase):

    def test_metric_granularity_adjustment_based_on_duration(self):
        hour = 3600
        day = 24 * 3600
        test_durations = [
            # passed duration, expected granularity
            (1 * hour, 300),
            (3 * hour, 300),
            (6 * hour, 600),
            (9 * hour, 600),
            (12 * hour, 1200),
            (1 * day, 1 * hour),
            (3 * day, 3 * hour),
            (7 * day, 6 * hour),
            (14 * day, 6 * hour),
        ]
        adjust_granularity = CloudWatchAPIMixin.modify_granularity
        for duration, expected_granularity in test_durations:
            granularity = adjust_granularity(duration)
            self.assertEqual(granularity, expected_granularity)
