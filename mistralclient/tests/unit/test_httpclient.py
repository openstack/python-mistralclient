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

import base64
import copy

import mock
from six.moves.urllib import parse as urlparse

from oslo_utils import uuidutils
from osprofiler import _utils as osprofiler_utils
import osprofiler.profiler

from mistralclient.api import httpclient
from mistralclient.tests.unit import base

API_BASE_URL = 'http://localhost:8989/v2'
API_URL = '/executions'

EXPECTED_URL = API_BASE_URL + API_URL

AUTH_TOKEN = uuidutils.generate_uuid()
PROJECT_ID = uuidutils.generate_uuid()
USER_ID = uuidutils.generate_uuid()
REGION_NAME = 'fake_region'
PROFILER_HMAC_KEY = 'SECRET_HMAC_KEY'
PROFILER_TRACE_ID = uuidutils.generate_uuid()

EXPECTED_AUTH_HEADERS = {
    'x-auth-token': AUTH_TOKEN,
    'X-Project-Id': PROJECT_ID,
    'X-User-Id': USER_ID,
    'X-Region-Name': REGION_NAME
}

EXPECTED_REQ_OPTIONS = {
    'headers': EXPECTED_AUTH_HEADERS
}

EXPECTED_BODY = {
    'k1': 'abc',
    'k2': 123,
    'k3': True
}


class HTTPClientTest(base.BaseClientTest):

    def setUp(self):
        super(HTTPClientTest, self).setUp()
        osprofiler.profiler.init(None)
        self.client = httpclient.HTTPClient(
            API_BASE_URL,
            auth_token=AUTH_TOKEN,
            project_id=PROJECT_ID,
            user_id=USER_ID,
            region_name=REGION_NAME
        )

    def assertExpectedAuthHeaders(self):
        headers = self.requests_mock.last_request.headers

        self.assertEqual(AUTH_TOKEN, headers['X-Auth-Token'])
        self.assertEqual(PROJECT_ID, headers['X-Project-Id'])
        self.assertEqual(USER_ID, headers['X-User-Id'])

        return headers

    def assertExpectedBody(self):
        text = self.requests_mock.last_request.text
        form = urlparse.parse_qs(text, strict_parsing=True)

        self.assertEqual(len(EXPECTED_BODY), len(form))

        for k, v in EXPECTED_BODY.items():
            self.assertEqual([str(v)], form[k])

        return form

    def test_get_request_options(self):
        m = self.requests_mock.get(EXPECTED_URL, text='text')

        self.client.get(API_URL)

        self.assertTrue(m.called_once)
        self.assertExpectedAuthHeaders()

    @mock.patch.object(
        osprofiler.profiler._Profiler,
        'get_base_id',
        mock.MagicMock(return_value=PROFILER_TRACE_ID)
    )
    @mock.patch.object(
        osprofiler.profiler._Profiler,
        'get_id',
        mock.MagicMock(return_value=PROFILER_TRACE_ID)
    )
    def test_get_request_options_with_profile_enabled(self):
        m = self.requests_mock.get(EXPECTED_URL, text='text')
        osprofiler.profiler.init(PROFILER_HMAC_KEY)

        data = {'base_id': PROFILER_TRACE_ID, 'parent_id': PROFILER_TRACE_ID}
        signed_data = osprofiler_utils.signed_pack(data, PROFILER_HMAC_KEY)

        headers = {
            'X-Trace-Info': signed_data[0],
            'X-Trace-HMAC': signed_data[1]
        }

        self.client.get(API_URL)

        self.assertTrue(m.called_once)
        headers = self.assertExpectedAuthHeaders()
        self.assertEqual(signed_data[0], headers['X-Trace-Info'])
        self.assertEqual(signed_data[1], headers['X-Trace-HMAC'])

    def test_get_request_options_with_headers_for_get(self):
        m = self.requests_mock.get(EXPECTED_URL, text='text')
        target_auth_url = uuidutils.generate_uuid()
        target_auth_token = uuidutils.generate_uuid()
        target_user_id = 'target_user'
        target_project_id = 'target_project'
        target_service_catalog = 'this should be there'
        target_insecure = 'target insecure'
        target_region = 'target region name'
        target_user_domain_name = 'target user domain name'
        target_project_domain_name = 'target project domain name'

        target_client = httpclient.HTTPClient(
            API_BASE_URL,
            auth_token=AUTH_TOKEN,
            project_id=PROJECT_ID,
            user_id=USER_ID,
            region_name=REGION_NAME,
            target_auth_url=target_auth_url,
            target_auth_token=target_auth_token,
            target_project_id=target_project_id,
            target_user_id=target_user_id,
            target_service_catalog=target_service_catalog,
            target_region_name=target_region,
            target_user_domain_name=target_user_domain_name,
            target_project_domain_name=target_project_domain_name,
            target_insecure=target_insecure
        )

        target_client.get(API_URL)

        self.assertTrue(m.called_once)
        headers = self.assertExpectedAuthHeaders()
        self.assertEqual(target_auth_url, headers['X-Target-Auth-Uri'])
        self.assertEqual(target_auth_token, headers['X-Target-Auth-Token'])
        self.assertEqual(target_user_id, headers['X-Target-User-Id'])
        self.assertEqual(target_project_id, headers['X-Target-Project-Id'])
        self.assertEqual(str(target_insecure), headers['X-Target-Insecure'])
        self.assertEqual(target_region, headers['X-Target-Region-Name'])
        self.assertEqual(target_user_domain_name,
                         headers['X-Target-User-Domain-Name'])
        self.assertEqual(target_project_domain_name,
                         headers['X-Target-Project-Domain-Name'])

        catalog = base64.b64encode(target_service_catalog.encode('utf-8'))
        self.assertEqual(catalog, headers['X-Target-Service-Catalog'])

    def test_get_request_options_with_headers_for_post(self):
        m = self.requests_mock.post(EXPECTED_URL, text='text')
        headers = {'foo': 'bar'}

        self.client.post(API_URL, EXPECTED_BODY, headers=headers)

        self.assertTrue(m.called_once)
        headers = self.assertExpectedAuthHeaders()
        self.assertEqual('application/json', headers['Content-Type'])
        self.assertEqual('bar', headers['foo'])
        self.assertExpectedBody()

    def test_get_request_options_with_headers_for_put(self):
        m = self.requests_mock.put(EXPECTED_URL, text='text')
        headers = {'foo': 'bar'}

        self.client.put(API_URL, EXPECTED_BODY, headers=headers)

        self.assertTrue(m.called_once)
        headers = self.assertExpectedAuthHeaders()
        self.assertEqual('application/json', headers['Content-Type'])
        self.assertEqual('bar', headers['foo'])
        self.assertExpectedBody()

    def test_get_request_options_with_headers_for_delete(self):
        m = self.requests_mock.delete(EXPECTED_URL, text='text')
        headers = {'foo': 'bar'}

        self.client.delete(API_URL, headers=headers)

        self.assertTrue(m.called_once)
        headers = self.assertExpectedAuthHeaders()
        self.assertEqual('bar', headers['foo'])

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_get(self):
        m = self.requests_mock.get(EXPECTED_URL, text='text')
        self.client.get(API_URL)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'get',
            None
        )
        self.assertTrue(m.called_once)
        self.assertExpectedAuthHeaders()

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_post(self):
        m = self.requests_mock.post(EXPECTED_URL, status_code=201, text='text')
        self.client.post(API_URL, EXPECTED_BODY)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'post',
            None
        )

        self.assertTrue(m.called_once)
        self.assertExpectedAuthHeaders()
        self.assertExpectedBody()

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_put(self):
        m = self.requests_mock.put(EXPECTED_URL, json={})
        self.client.put(API_URL, EXPECTED_BODY)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'put',
            None
        )

        self.assertTrue(m.called_once)
        self.assertExpectedAuthHeaders()
        self.assertExpectedBody()

    @mock.patch.object(
        httpclient.HTTPClient,
        '_get_request_options',
        mock.MagicMock(return_value=copy.deepcopy(EXPECTED_REQ_OPTIONS))
    )
    def test_http_delete(self):
        m = self.requests_mock.delete(EXPECTED_URL, text='text')
        self.client.delete(API_URL)

        httpclient.HTTPClient._get_request_options.assert_called_with(
            'delete',
            None
        )

        self.assertTrue(m.called_once)
        self.assertExpectedAuthHeaders()
