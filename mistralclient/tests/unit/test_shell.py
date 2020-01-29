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

    def test_help(self):
        """Test that client is not created for help and bash complete"""
        for command in ('-h',
                        '--help',
                        'help',
                        'help workbook-list',
                        'bash-completion'):
            with mock.patch('mistralclient.api.client.client') as client_mock:
                self.shell(command)
                self.assertFalse(client_mock.called)

    @mock.patch('mistralclient.api.client.client')
    def test_command_no_mistral_url(self, client_mock):
        self.shell(
            'workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('', params[1]['mistral_url'])

    @mock.patch('mistralclient.api.client.client')
    def test_command_interactive_mode(self, client_mock):
        self.shell('')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('', params[1]['mistral_url'])

    @mock.patch('mistralclient.api.client.client')
    def test_command_with_mistral_url(self, client_mock):
        self.shell(
            '--os-mistral-url=http://localhost:8989/v2 workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('http://localhost:8989/v2',
                         params[1]['mistral_url'])

    @mock.patch('mistralclient.api.client.determine_client_version')
    def test_mistral_version(self, client_mock):
        self.shell(
            '--os-mistral-version=v1 workbook-list'
        )
        self.assertTrue(client_mock.called)
        mistral_version = client_mock.call_args
        self.assertEqual('v1', mistral_version[0][0])

    @mock.patch('mistralclient.api.client.determine_client_version')
    def test_no_mistral_version(self, client_mock):
        self.shell('workbook-list')
        self.assertTrue(client_mock.called)
        mistral_version = client_mock.call_args
        self.assertEqual('v2', mistral_version[0][0])

    @mock.patch('mistralclient.api.client.client')
    def test_service_type(self, client_mock):
        self.shell('--os-mistral-service-type=test workbook-list')
        self.assertTrue(client_mock.called)
        parmters = client_mock.call_args
        self.assertEqual('test', parmters[1]['service_type'])

    @mock.patch('mistralclient.api.client.client')
    def test_no_service_type(self, client_mock):
        self.shell('workbook-list')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('workflowv2', params[1]['service_type'])

    @mock.patch('mistralclient.api.client.client')
    def test_endpoint_type(self, client_mock):
        self.shell('--os-mistral-endpoint-type=adminURL workbook-list')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('adminURL', params[1]['endpoint_type'])

    @mock.patch('mistralclient.api.client.client')
    def test_no_endpoint_type(self, client_mock):
        self.shell('workbook-list')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('publicURL', params[1]['endpoint_type'])

    @mock.patch('mistralclient.api.client.client')
    def test_auth_url(self, client_mock):
        self.shell(
            '--os-auth-url=https://127.0.0.1:35357/v3 '
            '--os-username=admin '
            '--os-password=1234 '
            'workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('https://127.0.0.1:35357/v3', params[1]['auth_url'])

    @mock.patch('mistralclient.api.client.client')
    def test_no_auth_url(self, client_mock):
        self.shell('workbook-list')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('', params[1]['auth_url'])

    @mock.patch('mistralclient.api.client.client')
    def test_default_auth_url_with_os_password(self, client_mock):
        self.shell('--os-username=admin --os-password=1234 workbook-list')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('http://localhost:35357/v3', params[1]['auth_url'])

    @mock.patch('mistralclient.api.client.client')
    def test_default_auth_url_with_os_auth_token(self, client_mock):
        self.shell(
            '--os-auth-token=abcd1234 '
            'workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('http://localhost:35357/v3', params[1]['auth_url'])

    @mock.patch('mistralclient.api.client.client')
    def test_profile(self, client_mock):
        self.shell('--profile=SECRET_HMAC_KEY workbook-list')
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('SECRET_HMAC_KEY', params[1]['profile'])

    @mock.patch('mistralclient.api.client.client')
    def test_region_name(self, client_mock):
        self.shell('--os-region-name=RegionOne workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args

        self.assertEqual('RegionOne', params[1]['region_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_tenant_id_and_tenant_name(self, client_mock):
        self.shell(
            '--os-tenant-id=123tenant --os-tenant-name=fake_tenant'
            ' workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('fake_tenant', params[1]['project_name'])
        self.assertEqual('123tenant', params[1]['project_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_project_id_and_project_name(self, client_mock):
        self.shell(
            '--os-project-name=fake_tenant --os-project-id=123tenant'
            ' workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args

        self.assertEqual('fake_tenant', params[1]['project_name'])
        self.assertEqual('123tenant', params[1]['project_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_project_domain_name(self, client_mock):
        self.shell('--os-project-domain-name=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args

        self.assertEqual('default', params[1]['project_domain_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_project_domain_id(self, client_mock):
        self.shell('--os-project-domain-id=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args

        self.assertEqual('default', params[1]['project_domain_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_user_domain_name(self, client_mock):
        self.shell('--os-user-domain-name=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('default', params[1]['user_domain_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_user_domain_id(self, client_mock):
        self.shell('--os-user-domain-id=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('default', params[1]['user_domain_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_target_user_name_and_password(self, client_mock):
        self.shell(
            '--os-target-username=admin'
            ' --os-target-password=secret_pass workbook-list')
        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('admin', params[1]['target_username'])
        self.assertEqual('secret_pass', params[1]['target_api_key'])

    @mock.patch('mistralclient.api.client.client')
    def test_target_tenant_name_and_id(self, client_mock):
        self.shell(
            '--os-target-tenant-id=123fake'
            ' --os-target-tenant-name=fake_target workbook-list')
        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('123fake', params[1]['target_project_id'])
        self.assertEqual('fake_target', params[1]['target_project_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_target_user_domain_id(self, client_mock):
        self.shell('--os-target-user-domain-id=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('default', params[1]['target_user_domain_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_target_user_domain_name(self, client_mock):
        self.shell('--os-target-user-domain-name=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('default', params[1]['target_user_domain_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_target_project_domain_id(self, client_mock):
        self.shell('--os-target-project-domain-id=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('default', params[1]['target_project_domain_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_target_project_domain_name(self, client_mock):
        self.shell('--os-target-project-domain-name=default workbook-list')

        self.assertTrue(client_mock.called)

        params = client_mock.call_args
        self.assertEqual('default', params[1]['target_project_domain_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_no_domains_keystone_v3(self, client_mock):
        self.shell(
            '--os-auth-url=https://127.0.0.1:35357/v3 '
            '--os-username=admin '
            '--os-password=1234 '
            'workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('https://127.0.0.1:35357/v3', params[1]['auth_url'])
        # For keystone v3 'default' values are automatically substituted for
        # project_domain_id and user_domain_id, if nothing was provided
        self.assertEqual('default', params[1]['project_domain_id'])
        self.assertEqual('default', params[1]['user_domain_id'])
        self.assertEqual('default', params[1]['target_project_domain_id'])
        self.assertEqual('default', params[1]['target_user_domain_id'])

    @mock.patch('mistralclient.api.client.client')
    def test_with_domain_names_keystone_v3(self, client_mock):
        self.shell(
            '--os-auth-url=https://127.0.0.1:35357/v3 '
            '--os-username=admin '
            '--os-password=1234 '
            '--os-project-domain-name=fake_domain '
            '--os-user-domain-name=fake_domain '
            '--os-target-project-domain-name=fake_domain '
            '--os-target-user-domain-name=fake_domain '
            'workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('https://127.0.0.1:35357/v3', params[1]['auth_url'])
        # No need to substitute values for project_domain_id and
        # user_domain_id if related domain names were provided
        self.assertEqual('', params[1]['project_domain_id'])
        self.assertEqual('', params[1]['user_domain_id'])
        self.assertEqual('fake_domain', params[1]['project_domain_name'])
        self.assertEqual('fake_domain', params[1]['user_domain_name'])
        self.assertEqual(
            'fake_domain',
            params[1]['target_project_domain_name']
        )
        self.assertEqual('fake_domain', params[1]['target_user_domain_name'])

    @mock.patch('mistralclient.api.client.client')
    def test_no_domains_keystone_v2(self, client_mock):
        self.shell(
            '--os-auth-url=https://127.0.0.1:35357/v2.0 '
            '--os-username=admin '
            '--os-password=1234 '
            'workbook-list'
        )
        self.assertTrue(client_mock.called)
        params = client_mock.call_args
        self.assertEqual('https://127.0.0.1:35357/v2.0', params[1]['auth_url'])
        # For keystone v2 nothing is substituted
        self.assertEqual('', params[1]['project_domain_id'])
        self.assertEqual('', params[1]['user_domain_id'])
        self.assertEqual('', params[1]['target_project_domain_id'])
        self.assertEqual('', params[1]['target_user_domain_id'])
