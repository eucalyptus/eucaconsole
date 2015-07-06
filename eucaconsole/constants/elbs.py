# -*- coding: utf-8 -*-
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
Eucalyptus and AWS ELB constants

"""

ELB_BACKEND_CERTIFICATE_NAME_PREFIX = 'EucaConsole-BackendServerAuthPolicy'
ELB_PREDEFINED_SECURITY_POLICY_NAME_PREFIX = 'ELBSecurityPolicy'
ELB_CUSTOM_SECURITY_POLICY_NAME_PREFIX = 'ELB-CustomSecurityPolicy'

ELB_MONITORING_CHARTS_LIST = [
    {
        'metric': 'RequestCount',
        'unit': 'Count',
        'statistic': 'Sum',
    },
    {
        'metric': 'Latency',
        'unit': 'Seconds',
        'statistic': 'Average',
    },
    {
        'metric': 'UnHealthyHostCount',
        'unit': 'Count',
        'statistic': 'Maximum',
    },
    {
        'metric': 'HealthyHostCount',
        'unit': 'Count',
        'statistic': 'Maximum',
    },
    {
        'metric': 'HTTPCode_ELB_4XX',
        'unit': 'Count',
        'statistic': 'Sum',
    },
    {
        'metric': 'HTTPCode_ELB_5XX',
        'unit': 'Count',
        'statistic': 'Sum',
    },
    {
        'metric': 'HTTPCode_Backend_2XX',
        'unit': 'Count',
        'statistic': 'Sum',
    },
    {
        'metric': 'HTTPCode_Backend_3XX',
        'unit': 'Count',
        'statistic': 'Sum',
    },
    {
        'metric': 'HTTPCode_Backend_4XX',
        'unit': 'Count',
        'statistic': 'Sum',
    },
    {
        'metric': 'HTTPCode_Backend_5XX',
        'unit': 'Count',
        'statistic': 'Sum',
    },
]


SSL_CIPHERS = [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-AES128-SHA256',
    'ECDHE-RSA-AES128-SHA256',
    'ECDHE-ECDSA-AES128-SHA',
    'ECDHE-RSA-AES128-SHA',
    'DHE-RSA-AES128-SHA',
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES256-SHA384',
    'ECDHE-RSA-AES256-SHA384',
    'ECDHE-RSA-AES256-SHA',
    'ECDHE-ECDSA-AES256-SHA',
    'AES128-GCM-SHA256',
    'AES128-SHA256',
    'AES128-SHA',
    'AES256-GCM-SHA384',
    'AES256-SHA256',
    'AES256-SHA',
    'DHE-DSS-AES128-SHA',
    'CAMELLIA128-SHA',
    'EDH-RSA-DES-CBC3-SHA',
    'DES-CBC3-SHA',
    'ECDHE-RSA-RC4-SHA',
    'RC4-SHA',
    'ECDHE-ECDSA-RC4-SHA',
    'DHE-DSS-AES256-GCM-SHA384',
    'DHE-RSA-AES256-GCM-SHA384',
    'DHE-RSA-AES256-SHA256',
    'DHE-DSS-AES256-SHA256',
    'DHE-RSA-AES256-SHA',
    'DHE-DSS-AES256-SHA',
    'DHE-RSA-CAMELLIA256-SHA',
    'DHE-DSS-CAMELLIA256-SHA',
    'CAMELLIA256-SHA',
    'EDH-DSS-DES-CBC3-SHA',
    'DHE-DSS-AES128-GCM-SHA256',
    'DHE-RSA-AES128-GCM-SHA256',
    'DHE-RSA-AES128-SHA256',
    'DHE-DSS-AES128-SHA256',
    'DHE-RSA-CAMELLIA128-SHA',
    'DHE-DSS-CAMELLIA128-SHA',
    'ADH-AES128-GCM-SHA256',
    'ADH-AES128-SHA',
    'ADH-AES128-SHA256',
    'ADH-AES256-GCM-SHA384',
    'ADH-AES256-SHA',
    'ADH-AES256-SHA256',
    'ADH-CAMELLIA128-SHA',
    'ADH-CAMELLIA256-SHA',
    'ADH-DES-CBC3-SHA',
    'ADH-DES-CBC-SHA',
    'ADH-RC4-MD5',
    'ADH-SEED-SHA',
    'DES-CBC-SHA',
    'DHE-DSS-SEED-SHA',
    'DHE-RSA-SEED-SHA',
    'EDH-DSS-DES-CBC-SHA',
    'EDH-RSA-DES-CBC-SHA',
    'IDEA-CBC-SHA',
    'RC4-MD5',
    'SEED-SHA',
    'DES-CBC3-MD5',
    'DES-CBC-MD5',
]
