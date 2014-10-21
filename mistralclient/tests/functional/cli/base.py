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

from tempest_lib.cli import base

from tempest import config
from tempest import test

CONF = config.CONF


class MistralCLIAuth(base.ClientTestBase, test.BaseTestCase):

    _mistral_url = None

    def _get_clients(self):
        clients = base.CLIClient(
            CONF.identity.admin_username,
            CONF.identity.admin_password,
            CONF.identity.admin_tenant_name,
            CONF.identity.uri,
            CONF.cli.cli_dir)
        return clients

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
