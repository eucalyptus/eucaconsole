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
Constants for security groups

"""

RULE_PROTOCOL_CHOICES = (
    ('22', 'SSH (TCP port 22, for terminal access)'),
    ('3389', 'RDP (TCP port 3389, for Windows instances)'),
    ('80', 'HTTP (TCP port 80, for web servers)'),
    ('443', 'HTTPS (TCP port 443, for web servers)'),
    ('1433', 'MS SQL (TCP port 1433)'),
    ('3306', 'MySQL (TCP port 3306)'),
    ('110', 'POP3 (TCP port 110)'),
    ('995', 'POP3S (TCP port 995)'),
    ('389', 'LDAP (TCP port 389)'),
    ('143', 'IMAP (TCP port 143)'),
    ('465', 'SMTP (TCP port 465)'),
    ('tcp', 'Custom TCP'),
    ('udp', 'Custom UDP'),
    ('icmp', 'Custom ICMP'),
)


RULE_ICMP_CHOICES = (
    ('0', 'Echo reply'),
    ('3', 'Destination unreachable'),
    ('4', 'Source quench'),
    ('5', 'Redirect message'),
    ('6', 'Alternate host address'),
    ('8', 'Echo request'),
    ('9', 'Router advertisement'),
    ('10', 'Router solicitation'),
    ('11', 'Timeout exceeded'),
    ('12', 'Parameter problem: Bad IP header'),
    ('13', 'Timestamp'),
    ('14', 'Timestamp reply'),
    ('15', 'Information request'),
    ('16', 'Infromation reply'),
    ('17', 'Address mask request'),
    ('18', 'Address mask reply'),
    ('30', 'Traceroute'),
    ('31', 'Diagram conversion error'),
    ('32', 'Mobile host redirect'),
    ('33', 'Where are you'),
    ('34', 'Here I am'),
    ('35', 'Mobile registration request'),
    ('36', 'Mobile registration reply'),
    ('37', 'Domain name request'),
    ('38', 'Domain name reply'),
    ('39', 'SKIP algorithm discovery protocol'),
    ('40', 'Photuris, security failures'),
    ('-1', 'All'),
)

