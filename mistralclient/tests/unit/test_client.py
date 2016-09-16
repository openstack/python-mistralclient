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
from oslotest import base

import osprofiler.profiler

from mistralclient.api import client

AUTH_HTTP_URL_v3 = 'http://localhost:35357/v3'
AUTH_HTTP_URL_v2_0 = 'http://localhost:35357/v2.0'
AUTH_HTTPS_URL = AUTH_HTTP_URL_v3.replace('http', 'https')
MISTRAL_HTTP_URL = 'http://localhost:8989/v2'
MISTRAL_HTTPS_URL = MISTRAL_HTTP_URL.replace('http', 'https')
PROFILER_HMAC_KEY = 'SECRET_HMAC_KEY'


class BaseClientTests(base.BaseTestCase):

    @mock.patch('keystoneclient.v2_0.client.Client')
    def test_mistral_url_from_catalog_v2(self, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        url_for = mock.Mock(return_value='http://mistral_host:8989/v2')

        keystone_client_instance.service_catalog.url_for = url_for

        mistralclient = client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v2_0,
            service_type='workflowv2'
        )

        self.assertEqual(
            'http://mistral_host:8989/v2',
            mistralclient.actions.http_client.base_url
        )

    @mock.patch('keystoneclient.v3.client.Client')
    def test_mistral_url_from_catalog(self, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())

        url_for = mock.Mock(return_value='http://mistral_host:8989/v2')

        keystone_client_instance.service_catalog.url_for = url_for

        mistralclient = client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3,
            service_type='workflowv2'
        )

        self.assertEqual(
            'http://mistral_host:8989/v2',
            mistralclient.actions.http_client.base_url
        )

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_default(self, mocked, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())
        url_for = mock.Mock(side_effect=Exception)
        keystone_client_instance.service_catalog.url_for = url_for

        expected_args = (
            MISTRAL_HTTP_URL,
        )

        expected_kwargs = {
            'username': 'mistral',
            'project_name': 'mistral',
            'auth_url': AUTH_HTTP_URL_v3,
            'auth_token': keystone_client_instance.auth_token,
            'project_id': keystone_client_instance.project_id,
            'user_id': keystone_client_instance.user_id
        }

        client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3
        )

        self.assertTrue(mocked.called)
        self.assertEqual(expected_args, mocked.call_args[0])
        self.assertDictEqual(expected_kwargs, mocked.call_args[1])

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_insecure(self, mocked, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())
        url_for = mock.Mock(side_effect=Exception)
        keystone_client_instance.service_catalog.url_for = url_for

        expected_args = (
            MISTRAL_HTTPS_URL,
        )

        expected_kwargs = {
            'mistral_url': MISTRAL_HTTPS_URL,
            'username': 'mistral',
            'project_name': 'mistral',
            'auth_url': AUTH_HTTP_URL_v3,
            'cacert': None,
            'insecure': True,
            'auth_token': keystone_client_instance.auth_token,
            'project_id': keystone_client_instance.project_id,
            'user_id': keystone_client_instance.user_id
        }

        client.client(
            mistral_url=MISTRAL_HTTPS_URL,
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3,
            cacert=None,
            insecure=True
        )

        self.assertTrue(mocked.called)
        self.assertEqual(expected_args, mocked.call_args[0])
        self.assertDictEqual(expected_kwargs, mocked.call_args[1])

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
        )

        expected_kwargs = {
            'mistral_url': MISTRAL_HTTPS_URL,
            'username': 'mistral',
            'project_name': 'mistral',
            'auth_url': AUTH_HTTP_URL_v3,
            'cacert': path,
            'insecure': False,
            'auth_token': keystone_client_instance.auth_token,
            'project_id': keystone_client_instance.project_id,
            'user_id': keystone_client_instance.user_id
        }

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                username='mistral',
                project_name='mistral',
                auth_url=AUTH_HTTP_URL_v3,
                cacert=path,
                insecure=False
            )
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(mock.called)
        self.assertEqual(expected_args, mock.call_args[0])
        self.assertDictEqual(expected_kwargs, mock.call_args[1])

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
            auth_url=AUTH_HTTP_URL_v3,
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
                auth_url=AUTH_HTTP_URL_v3,
                cacert=path,
                insecure=True
            )
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(log_warning_mock.called)

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_profile_enabled(self, mocked, keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())
        url_for = mock.Mock(side_effect=Exception)
        keystone_client_instance.service_catalog.url_for = url_for

        expected_args = (
            MISTRAL_HTTP_URL,
        )

        expected_kwargs = {
            'username': 'mistral',
            'project_name': 'mistral',
            'auth_url': AUTH_HTTP_URL_v3,
            'profile': PROFILER_HMAC_KEY,
            'auth_token': keystone_client_instance.auth_token,
            'project_id': keystone_client_instance.project_id,
            'user_id': keystone_client_instance.user_id
        }

        client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3,
            profile=PROFILER_HMAC_KEY
        )

        self.assertTrue(mocked.called)
        self.assertEqual(expected_args, mocked.call_args[0])
        self.assertDictEqual(expected_kwargs, mocked.call_args[1])

        profiler = osprofiler.profiler.get()

        self.assertEqual(profiler.hmac_key, PROFILER_HMAC_KEY)
