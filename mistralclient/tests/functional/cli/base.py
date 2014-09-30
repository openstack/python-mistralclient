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

from tempest import cli


class MistralCLIAuth(cli.ClientTestBase):

    _mistral_url = None

    def mistral(self, action, flags='', params='', admin=True, fail_ok=False,
                keystone_version=3):
        """Executes Mistral command."""
        mistral_url_op = "--os-mistral-url %s" % self._mistral_url

        if 'WITHOUT_AUTH' in os.environ:
            return cli.execute(
                'mistral %s' % mistral_url_op, action, flags, params)
        else:
            return self.cmd_with_auth(
                'mistral %s' % mistral_url_op, action, flags, params, admin,
                fail_ok, keystone_version)
