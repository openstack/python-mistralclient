# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
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

from unittest import mock

from mistralclient.api.v2 import client
from mistralclient.tests.unit import base


class BaseClientV2Test(base.BaseClientTest):

    TEST_URL = 'http://mistral.example.com'

    def setUp(self):
        super(BaseClientV2Test, self).setUp()

        with mock.patch(
                'mistralclient.auth.keystone.KeystoneAuthHandler.authenticate',
                return_value={'session': None}):
            self._client = client.Client(project_name="test",
                                         mistral_url=self.TEST_URL)
            self.workbooks = self._client.workbooks
            self.executions = self._client.executions
            self.tasks = self._client.tasks
            self.workflows = self._client.workflows
            self.environments = self._client.environments
            self.action_executions = self._client.action_executions
            self.actions = self._client.actions
            self.services = self._client.services
            self.members = self._client.members
