# Copyright (c) 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

import os_client_config
from tempest.lib.cli import base


CLI_DIR = os.environ.get(
    'OS_MISTRALCLIENT_EXEC_DIR',
    os.path.join(os.path.abspath('.'), '.tox/functional/bin')
)


def credentials(cloud='devstack-admin'):
    """Retrieves credentials to run functional tests

    Credentials are either read via os-client-config from the environment
    or from a config file ('clouds.yaml'). Environment variables override
    those from the config file.
    devstack produces a clouds.yaml with two named clouds - one named
    'devstack' which has user privs and one named 'devstack-admin' which
    has admin privs. This function will default to getting the devstack-admin
    cloud as that is the current expected behavior.
    """
    return get_cloud_config(cloud=cloud).get_auth_args()


def get_cloud_config(cloud='devstack-admin'):
    return os_client_config.OpenStackConfig().get_one_cloud(cloud=cloud)


class MistralCLIAuth(base.ClientTestBase):

    _mistral_url = None

    def _get_admin_clients(self):
        creds = credentials()

        clients = base.CLIClient(
            username=creds['username'],
            password=creds['password'],
            tenant_name=creds['project_name'],
            project_name=creds['project_name'],
            user_domain_id=creds['user_domain_id'],
            project_domain_id=creds['project_domain_id'],
            uri=creds['auth_url'],
            cli_dir=CLI_DIR
        )

        return clients

    def _get_clients(self):
        return self._get_admin_clients()

    def mistral(self, action, flags='', params='', fail_ok=False):
        """Executes Mistral command."""
        mistral_url_op = "--os-mistral-url %s" % self._mistral_url
        flags = "{} --insecure".format(flags)

        if 'WITHOUT_AUTH' in os.environ:
            return base.execute(
                'mistral %s' % mistral_url_op,
                action,
                flags,
                params,
                fail_ok,
                merge_stderr=False,
                cli_dir=''
            )
        else:
            return self.clients.cmd_with_auth(
                'mistral %s' % mistral_url_op,
                action,
                flags,
                params,
                fail_ok
            )

    def get_project_id(self, project_name='admin'):
        admin_clients = self._get_clients()

        projects = self.parser.listing(
            admin_clients.openstack(
                'project show',
                params=project_name,
                flags='--os-identity-api-version 3 --insecure'
            )
        )

        return [o['Value'] for o in projects if o['Field'] == 'id'][0]


class MistralCLIAltAuth(base.ClientTestBase):

    _mistral_url = None

    def _get_alt_clients(self):
        creds = credentials('devstack-alt-member')

        clients = base.CLIClient(
            username=creds['username'],
            password=creds['password'],
            project_name=creds['project_name'],
            tenant_name=creds['project_name'],
            user_domain_id=creds['user_domain_id'],
            project_domain_id=creds['project_domain_id'],
            uri=creds['auth_url'],
            cli_dir=CLI_DIR
        )

        return clients

    def _get_clients(self):
        return self._get_alt_clients()

    def mistral_alt(self, action, flags='', params='', mode='alt_user'):
        """Executes Mistral command for alt_user from alt_tenant."""
        mistral_url_op = "--os-mistral-url %s" % self._mistral_url
        flags = "{} --insecure".format(flags)

        return self.clients.cmd_with_auth(
            'mistral %s' % mistral_url_op, action, flags, params)
