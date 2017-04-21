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
Eucalyptus and AWS S3 constants

"""

SAMPLE_CORS_CONFIGURATION = """
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3600</MaxAgeSeconds>
        <AllowedHeader>Authorization</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
"""

SAMPLE_BUCKET_POLICY_TEMPLATE = """
{
  "Statement":[
    {
      "Action":["s3:PutObject"],
      "Effect":"Allow",
      "Principal": {"AWS":"${account_id}"},
      "Resource":["arn:aws:s3:::${bucket_name}/*"],
      "Sid":"SampleBucketPolicy"
    }
  ],
  "Version":"2012-10-17"
}
"""

# CORS RelaxNG Schema Definition
# See http://relaxng.org/tutorial-20011203.html
# See http://docs.aws.amazon.com/AmazonS3/latest/dev/cors.html
#
# NOTE: This schema does not include the "http://s3.amazonaws.com/doc/2006-03-01/" namespace declaration,
#       so any CORS XML validated against this schema will need namespaces removed
#
CORS_XML_RELAXNG_SCHEMA = """
<element name="CORSConfiguration" xmlns="http://relaxng.org/ns/structure/1.0">
  <oneOrMore>
    <element name="CORSRule">
      <interleave>
        <oneOrMore>
          <element name="AllowedOrigin"><text /></element>
        </oneOrMore>
        <oneOrMore>
          <element name="AllowedMethod">
            <choice>
              <value>GET</value>
              <value>PUT</value>
              <value>POST</value>
              <value>DELETE</value>
              <value>HEAD</value>
            </choice>
          </element>
        </oneOrMore>
        <zeroOrMore>
          <element name="AllowedHeader"><text /></element>
        </zeroOrMore>
        <zeroOrMore>
          <element name="ExposeHeader"><text /></element>
        </zeroOrMore>
        <optional>
          <element name="MaxAgeSeconds">
            <data type="nonNegativeInteger" datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes"/>
          </element>
        </optional>
        <optional>
          <element name="ID"><text /></element>
        </optional>
      </interleave>
    </element>
  </oneOrMore>
</element>
"""
