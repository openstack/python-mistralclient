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

from six.moves import configparser
from tempest_lib.cli import base


CLI_DIR = os.environ.get(
    'OS_MISTRALCLIENT_EXEC_DIR',
    os.path.join(os.path.abspath('.'), '.tox/functional/bin')
)
_CREDS_FILE = 'functional_creds.conf'


def credentials(group='admin'):
    """Retrieves credentials to run functional tests.

    Credentials are either read from the environment or from a config file
    ('functional_creds.conf'). Environment variables override those from the
    config file.

    The 'functional_creds.conf' file is the clean and new way to use (by
    default tox 2.0 does not pass environment variables).
    """
    if group == 'admin':
        username = os.environ.get('OS_USERNAME')
        password = os.environ.get('OS_PASSWORD')
        tenant_name = os.environ.get('OS_TENANT_NAME')
    else:
        username = os.environ.get('OS_ALT_USERNAME')
        password = os.environ.get('OS_ALT_PASSWORD')
        tenant_name = os.environ.get('OS_ALT_TENANT_NAME')

    auth_url = os.environ.get('OS_AUTH_URL')

    config = configparser.RawConfigParser()
    if config.read(_CREDS_FILE):
        username = username or config.get(group, 'user')
        password = password or config.get(group, 'pass')
        tenant_name = tenant_name or config.get(group, 'tenant')
        auth_url = auth_url or config.get('auth', 'uri')

    return {
        'username': username,
        'password': password,
        'tenant_name': tenant_name,
        'auth_url': auth_url
    }


class MistralCLIAuth(base.ClientTestBase):

    _mistral_url = None

    def _get_admin_clients(self):
        creds = credentials()

        clients = base.CLIClient(
            username=creds['username'],
            password=creds['password'],
            tenant_name=creds['tenant_name'],
            uri=creds['auth_url'],
            cli_dir=CLI_DIR
        )

        return clients

    def _get_clients(self):
        return self._get_admin_clients()

    def mistral(self, action, flags='', params='', fail_ok=False):
        """Executes Mistral command."""
        mistral_url_op = "--os-mistral-url %s" % self._mistral_url

        if 'WITHOUT_AUTH' in os.environ:
            return base.execute(
                'mistral %s' % mistral_url_op, action, flags, params,
                fail_ok, merge_stderr=False, cli_dir='')
        else:
            return self.clients.cmd_with_auth(
                'mistral %s' % mistral_url_op, action, flags, params,
                fail_ok)


class MistralCLIAltAuth(base.ClientTestBase):

    _mistral_url = None

    def _get_alt_clients(self):
        creds = credentials('demo')

        clients = base.CLIClient(
            username=creds['username'],
            password=creds['password'],
            tenant_name=creds['tenant_name'],
            uri=creds['auth_url'],
            cli_dir=CLI_DIR
        )

        return clients

    def _get_clients(self):
        return self._get_alt_clients()

    def mistral_alt(self, action, flags='', params='', mode='alt_user'):
        """Executes Mistral command for alt_user from alt_tenant."""
        mistral_url_op = "--os-mistral-url %s" % self._mistral_url

        return self.clients.cmd_with_auth(
            'mistral %s' % mistral_url_op, action, flags, params)
