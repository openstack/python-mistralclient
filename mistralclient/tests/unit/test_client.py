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

import mock
from oslo_utils import uuidutils
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
    def setup_keystone_mock(session_mock):
        keystone_client_instance = session_mock.return_value
        keystone_client_instance.auth_token = uuidutils.generate_uuid()
        keystone_client_instance.project_id = uuidutils.generate_uuid()
        keystone_client_instance.user_id = uuidutils.generate_uuid()
        keystone_client_instance.auth_ref = str(json.dumps({}))
        return keystone_client_instance

    @mock.patch('keystoneauth1.session.Session')
    def test_mistral_url_from_catalog_v2(self, session_mock):
        session = mock.Mock()
        session_mock.side_effect = [session]

        get_endpoint = mock.Mock(return_value='http://mistral_host:8989/v2')
        session.get_endpoint = get_endpoint

        mistralclient = client.client(
            username='mistral',
            project_name='mistral',
            api_key='password',
            auth_url=AUTH_HTTP_URL_v2_0,
            service_type='workflowv2'
        )

        self.assertEqual(
            'http://mistral_host:8989/v2',
            mistralclient.actions.http_client.base_url
        )

    @mock.patch('keystoneauth1.session.Session')
    def test_mistral_url_from_catalog(self, session_mock):
        session = mock.Mock()
        session_mock.side_effect = [session]

        get_endpoint = mock.Mock(return_value='http://mistral_host:8989/v2')
        session.get_endpoint = get_endpoint

        mistralclient = client.client(
            username='mistral',
            project_name='mistral',
            api_key='password',
            user_domain_name='Default',
            project_domain_name='Default',
            auth_url=AUTH_HTTP_URL_v3,
            service_type='workflowv2'
        )

        self.assertEqual(
            'http://mistral_host:8989/v2',
            mistralclient.actions.http_client.base_url
        )

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_default(self, http_client_mock, session_mock):
        session = mock.Mock()
        session_mock.side_effect = [session]

        get_endpoint = mock.Mock(side_effect=Exception)
        session.get_endpoint = get_endpoint

        client.client(
            username='mistral',
            project_name='mistral',
            api_key='password',
            user_domain_name='Default',
            project_domain_name='Default',
            auth_url=AUTH_HTTP_URL_v3
        )

        self.assertTrue(http_client_mock.called)
        mistral_url_for_http = http_client_mock.call_args[0][0]
        self.assertEqual(MISTRAL_HTTP_URL, mistral_url_for_http)

    @mock.patch('keystoneauth1.identity.generic.Password')
    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_target_parameters_processed(
        self,
        http_client_mock,
        session_mock,
        password_mock
    ):

        session = mock.MagicMock()
        target_session = mock.MagicMock()
        session_mock.side_effect = [session, target_session]
        auth = mock.MagicMock()
        password_mock.side_effect = [auth, auth]

        get_endpoint = mock.Mock(return_value='http://mistral_host:8989/v2')
        session.get_endpoint = get_endpoint

        target_session.get_project_id = mock.Mock(return_value='projectid')
        target_session.get_user_id = mock.Mock(return_value='userid')
        target_session.get_auth_headers = mock.Mock(return_value={
            'X-Auth-Token': 'authtoken'
        })

        mock_access = mock.MagicMock()
        mock_catalog = mock.MagicMock()
        mock_catalog.catalog = {}
        mock_access.service_catalog = mock_catalog
        auth.get_access = mock.Mock(return_value=mock_access)

        client.client(
            username='user',
            api_key='password',
            user_domain_name='Default',
            project_domain_name='Default',
            target_username='tmistral',
            target_project_name='tmistralp',
            target_auth_url=AUTH_HTTP_URL_v3,
            target_api_key='tpassword',
            target_user_domain_name='Default',
            target_project_domain_name='Default',
            target_region_name='tregion'
        )

        self.assertTrue(http_client_mock.called)
        mistral_url_for_http = http_client_mock.call_args[0][0]
        kwargs = http_client_mock.call_args[1]
        self.assertEqual('http://mistral_host:8989/v2', mistral_url_for_http)

        expected_values = {
            'target_project_id': 'projectid',
            'target_auth_token': 'authtoken',
            'target_user_id': 'userid',
            'target_auth_url': AUTH_HTTP_URL_v3,
            'target_project_name': 'tmistralp',
            'target_username': 'tmistral',
            'target_region_name': 'tregion',
            'target_service_catalog': "{}"
        }

        for key in expected_values:
            self.assertEqual(expected_values[key], kwargs[key])

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_insecure(self, http_client_mock, session_mock):
        keystone_client_instance = self.setup_keystone_mock(  # noqa
            session_mock
        )

        expected_args = (
            MISTRAL_HTTPS_URL,
        )

        client.client(
            mistral_url=MISTRAL_HTTPS_URL,
            username='mistral',
            project_name='mistral',
            api_key='password',
            user_domain_name='Default',
            project_domain_name='Default',
            auth_url=AUTH_HTTP_URL_v3,
            cacert=None,
            insecure=True
        )

        self.assertTrue(http_client_mock.called)
        self.assertEqual(http_client_mock.call_args[0], expected_args)
        self.assertEqual(http_client_mock.call_args[1]['insecure'], True)

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_url_https_secure(self, http_client_mock, session_mock):
        fd, cert_path = tempfile.mkstemp(suffix='.pem')

        keystone_client_instance = self.setup_keystone_mock(  # noqa
            session_mock
        )

        expected_args = (
            MISTRAL_HTTPS_URL,
        )

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                username='mistral',
                project_name='mistral',
                api_key='password',
                user_domain_name='Default',
                project_domain_name='Default',
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

    @mock.patch('keystoneauth1.session.Session')
    def test_mistral_url_https_bad_cacert(self, session_mock):
        keystone_client_instance = self.setup_keystone_mock(  # noqa
            session_mock
        )

        self.assertRaises(
            ValueError,
            client.client,
            mistral_url=MISTRAL_HTTPS_URL,
            username='mistral',
            project_name='mistral',
            api_key='password',
            user_domain_name='Default',
            project_domain_name='Default',
            auth_url=AUTH_HTTP_URL_v3,
            cacert='/path/to/foobar',
            insecure=False
        )

    @mock.patch('logging.Logger.warning')
    @mock.patch('keystoneauth1.session.Session')
    def test_mistral_url_https_bad_insecure(self, session_mock,
                                            log_warning_mock):
        fd, path = tempfile.mkstemp(suffix='.pem')

        keystone_client_instance = self.setup_keystone_mock(
            session_mock
        )

        try:
            client.client(
                mistral_url=MISTRAL_HTTPS_URL,
                user_id=keystone_client_instance.user_id,
                project_id=keystone_client_instance.project_id,
                api_key='password',
                user_domain_name='Default',
                project_domain_name='Default',
                auth_url=AUTH_HTTP_URL_v3,
                cacert=path,
                insecure=True
            )
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(log_warning_mock.called)

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('mistralclient.api.httpclient.HTTPClient')
    def test_mistral_profile_enabled(self, http_client_mock, session_mock):
        keystone_client_instance = self.setup_keystone_mock(  # noqa
            session_mock
        )

        client.client(
            username='mistral',
            project_name='mistral',
            api_key='password',
            user_domain_name='Default',
            project_domain_name='Default',
            auth_url=AUTH_HTTP_URL_v3,
            profile=PROFILER_HMAC_KEY
        )

        self.assertTrue(http_client_mock.called)

        profiler = osprofiler.profiler.get()

        self.assertEqual(profiler.hmac_key, PROFILER_HMAC_KEY)
