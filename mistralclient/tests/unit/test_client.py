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

import json
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

    @staticmethod
    def setup_keystone_mock(keystone_client_mock):
        keystone_client_instance = keystone_client_mock.return_value
        keystone_client_instance.auth_token = str(uuid.uuid4())
        keystone_client_instance.project_id = str(uuid.uuid4())
        keystone_client_instance.user_id = str(uuid.uuid4())
        keystone_client_instance.auth_ref = str(json.dumps({}))
        return keystone_client_instance

    @mock.patch('keystoneclient.v2_0.client.Client')
    def test_mistral_url_from_catalog_v2(self, keystone_client_mock):
        keystone_client_instance = self.setup_keystone_mock(
            keystone_client_mock
        )

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
        keystone_client_instance = self.setup_keystone_mock(
            keystone_client_mock
        )

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
    def test_mistral_url_default(self, http_client_mock, keystone_client_mock):
        keystone_client_instance = self.setup_keystone_mock(
            keystone_client_mock
        )

        url_for = mock.Mock(side_effect=Exception)
        keystone_client_instance.service_catalog.url_for = url_for

        client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3
        )

        self.assertTrue(http_client_mock.called)
        mistral_url_for_http = http_client_mock.call_args[0][0]
        kwargs = http_client_mock.call_args[1]
        self.assertEqual(MISTRAL_HTTP_URL, mistral_url_for_http)
        self.assertEqual(
            keystone_client_instance.auth_token, kwargs['auth_token']
        )
        self.assertEqual(
            keystone_client_instance.project_id, kwargs['project_id']
        )
        self.assertEqual(
            keystone_client_instance.user_id, kwargs['user_id']
        )

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_target_parameters_processed(
        self,
        http_client_mock,
        keystone_client_mock
    ):
        keystone_client_instance = self.setup_keystone_mock(
            keystone_client_mock
        )

        url_for = mock.Mock(return_value='http://mistral_host:8989/v2')
        keystone_client_instance.service_catalog.url_for = url_for

        client.client(
            target_username='tmistral',
            target_project_name='tmistralp',
            target_auth_url=AUTH_HTTP_URL_v3,
            target_region_name='tregion'
        )

        self.assertTrue(http_client_mock.called)
        mistral_url_for_http = http_client_mock.call_args[0][0]
        kwargs = http_client_mock.call_args[1]
        self.assertEqual(MISTRAL_HTTP_URL, mistral_url_for_http)

        expected_values = {
            'target_project_id': keystone_client_instance.project_id,
            'target_auth_token': keystone_client_instance.auth_token,
            'target_user_id': keystone_client_instance.user_id,
            'target_auth_url': AUTH_HTTP_URL_v3,
            'target_project_name': 'tmistralp',
            'target_username': 'tmistral',
            'target_region_name': 'tregion',
            'target_service_catalog': '"{}"'
        }

        for key in expected_values:
            self.assertEqual(expected_values[key], kwargs[key])

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_insecure(self, http_client_mock,
                                        keystone_client_mock):
        keystone_client_instance = self.setup_keystone_mock(  # noqa
            keystone_client_mock
        )

        expected_args = (
            MISTRAL_HTTPS_URL,
        )

        client.client(
            mistral_url=MISTRAL_HTTPS_URL,
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3,
            cacert=None,
            insecure=True
        )

        self.assertTrue(http_client_mock.called)
        self.assertEqual(http_client_mock.call_args[0], expected_args)
        self.assertEqual(http_client_mock.call_args[1]['insecure'], True)

    @mock.patch('keystoneclient.v3.client.Client')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_secure(self, http_client_mock,
                                      keystone_client_mock):
        fd, cert_path = tempfile.mkstemp(suffix='.pem')

        keystone_client_instance = self.setup_keystone_mock(  # noqa
            keystone_client_mock
        )

        expected_args = (
            MISTRAL_HTTPS_URL,
        )

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                username='mistral',
                project_name='mistral',
                auth_url=AUTH_HTTP_URL_v3,
                cacert=cert_path,
                insecure=False
            )
        finally:
            os.close(fd)
            os.unlink(cert_path)

        self.assertTrue(http_client_mock.called)
        self.assertEqual(http_client_mock.call_args[0], expected_args)
        self.assertEqual(http_client_mock.call_args[1]['cacert'], cert_path)

    @mock.patch('keystoneclient.v3.client.Client')
    def test_mistral_url_https_bad_cacert(self, keystone_client_mock):
        keystone_client_instance = self.setup_keystone_mock(  # noqa
            keystone_client_mock
        )

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

        keystone_client_instance = self.setup_keystone_mock(
            keystone_client_mock
        )

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                user_id=keystone_client_instance.user_id,
                project_id=keystone_client_instance.project_id,
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
    def test_mistral_profile_enabled(self, http_client_mock,
                                     keystone_client_mock):
        keystone_client_instance = self.setup_keystone_mock(  # noqa
            keystone_client_mock
        )

        client.client(
            username='mistral',
            project_name='mistral',
            auth_url=AUTH_HTTP_URL_v3,
            profile=PROFILER_HMAC_KEY
        )

        self.assertTrue(http_client_mock.called)

        profiler = osprofiler.profiler.get()

        self.assertEqual(profiler.hmac_key, PROFILER_HMAC_KEY)
