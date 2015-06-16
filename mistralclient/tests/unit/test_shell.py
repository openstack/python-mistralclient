# Copyright 2015 Huawei Technologies Co., Ltd.
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

import mock

import mistralclient.tests.unit.base_shell_test as base


class TestShell(base.BaseShellTests):

    @mock.patch('mistralclient.api.client.client')
    def test_command_no_mistral_url(self, mock):
        self.shell(
            'workbook-list'
        )
        self.assertTrue(mock.called)
        params = mock.call_args
        self.assertEqual(params[1]['mistral_url'], '')

    @mock.patch('mistralclient.api.client.client')
    def test_command_with_mistral_url(self, mock):
        self.shell(
            '--os-mistral-url=http://localhost:8989/v2 workbook-list'
        )
        self.assertTrue(mock.called)
        params = mock.call_args
        self.assertEqual(params[1]['mistral_url'],
                         'http://localhost:8989/v2')

    @mock.patch('mistralclient.api.client.determine_client_version')
    def test_mistral_version(self, mock):
        self.shell(
            '--os-mistral-version=v1 workbook-list'
        )
        self.assertTrue(mock.called)
        mistral_version = mock.call_args
        self.assertEqual(mistral_version[0][0], 'v1')

    @mock.patch('mistralclient.api.client.determine_client_version')
    def test_no_mistral_version(self, mock):
        self.shell('workbook-list')
        self.assertTrue(mock.called)
        mistral_version = mock.call_args
        self.assertEqual(mistral_version[0][0], 'v2')

    @mock.patch('mistralclient.api.client.client')
    def test_service_type(self, mock):
        self.shell('--os-mistral-service-type=test workbook-list')
        self.assertTrue(mock.called)
        parmters = mock.call_args
        self.assertEqual(parmters[1]['service_type'], 'test')

    @mock.patch('mistralclient.api.client.client')
    def test_no_service_type(self, mock):
        self.shell('workbook-list')
        self.assertTrue(mock.called)
        params = mock.call_args
        self.assertEqual(params[1]['service_type'], 'workflowv2')

    @mock.patch('mistralclient.api.client.client')
    def test_endpoint_type(self, mock):
        self.shell('--os-mistral-endpoint-type=adminURL workbook-list')
        self.assertTrue(mock.called)
        params = mock.call_args
        self.assertEqual(params[1]['endpoint_type'], 'adminURL')

    @mock.patch('mistralclient.api.client.client')
    def test_no_endpoint_type(self, mock):
        self.shell('workbook-list')
        self.assertTrue(mock.called)
        params = mock.call_args
        self.assertEqual(params[1]['endpoint_type'], 'publicURL')