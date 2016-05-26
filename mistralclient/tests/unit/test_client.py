# Copyright 2015 - Huawei Technologies Co., Ltd.
# Copyright 2016 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import tempfile
import uuid

import mock
import testtools

import osprofiler.profiler

from mistralclient.api import client

AUTH_HTTP_URL = 'http://localhost:35357/v3'
AUTH_HTTPS_URL = AUTH_HTTP_URL.replace('http', 'https')
MISTRAL_HTTP_URL = 'http://localhost:8989/v2'
MISTRAL_HTTPS_URL = MISTRAL_HTTP_URL.replace('http', 'https')
PROFILER_HMAC_KEY = 'SECRET_HMAC_KEY'


class BaseClientTests(testtools.TestCase):

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_default(self, mock, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        expected_args = (
            MISTRAL_HTTP_URL,
            keystone_client_instance.auth_token,
            keystone_client_instance.project_id,
            keystone_client_instance.user_id
        )

        expected_kwargs = {
            'cacert': None,
            'insecure': False
        }

        client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL
        )

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_insecure(self, mock, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        expected_args = (
            MISTRAL_HTTPS_URL,
            keystone_client_instance.auth_token,
            keystone_client_instance.project_id,
            keystone_client_instance.user_id
        )

        expected_kwargs = {
            'cacert': None,
            'insecure': True
        }

        client.client(
            mistral_url=MISTRAL_HTTPS_URL,
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL,
            cacert=None,
            insecure=True
        )

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_secure(self, mock, keystone_client_mock):
        fd, path = tempfile.mkstemp(suffix='.pem')

        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        expected_args = (
            MISTRAL_HTTPS_URL,
            keystone_client_instance.auth_token,
            keystone_client_instance.project_id,
            keystone_client_instance.user_id
        )

        expected_kwargs = {
            'cacert': path,
            'insecure': False
        }

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                username='mistral',
                project_name='mistral',
                auth_url=AUTH_HTTP_URL,
                cacert=path,
                insecure=False
            )
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

    @mock.patch('keystoneclient.v3.client.Client')
    def test_mistral_url_https_bad_cacert(self, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        self.assertRaises(
            ValueError,
            client.client,
            mistral_url=MISTRAL_HTTPS_URL,
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL,
            cacert='/path/to/foobar',
            insecure=False
        )

    @mock.patch('logging.Logger.warning')
    @mock.patch('keystoneclient.v3.client.Client')
    def test_mistral_url_https_bad_insecure(self, keystone_client_mock,
                                            log_warning_mock):
        fd, path = tempfile.mkstemp(suffix='.pem')

        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                username='mistral',
                project_name='mistral',
                auth_url=AUTH_HTTP_URL,
                cacert=path,
                insecure=True
            )
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(log_warning_mock.called)

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_profile_enabled(self, mock, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        expected_args = (
            MISTRAL_HTTP_URL,
            keystone_client_instance.auth_token,
            keystone_client_instance.project_id,
            keystone_client_instance.user_id
        )

        expected_kwargs = {
            'cacert': None,
            'insecure': False
        }

        client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL,
            profile=PROFILER_HMAC_KEY
        )

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

        profiler = osprofiler.profiler.get()

        self.assertEqual(profiler.hmac_key, PROFILER_HMAC_KEY)
