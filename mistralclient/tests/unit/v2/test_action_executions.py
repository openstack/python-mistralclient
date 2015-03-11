# Copyright 2014 - Mirantis, Inc.
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

from mistralclient.api.v2 import action_executions
from mistralclient.tests.unit.v2 import base

# TODO(everyone): later we need additional tests verifying all the errors etc.

ACTION_EXEC = {
    'id': "1",
    'name': 'my_action_execution',
    'workflow_name': 'my_wf',
    'state': 'RUNNING',
}


URL_TEMPLATE = '/action_executions'
URL_TEMPLATE_ID = '/action_executions/%s'


class TestActionExecutions(base.BaseClientV2Test):
    def test_update(self):
        mock = self.mock_http_put(content=ACTION_EXEC)
        body = {
            'state': ACTION_EXEC['state']
        }

        action_execution = self.action_executions.update(
            ACTION_EXEC['id'],
            ACTION_EXEC['state']
        )

        self.assertIsNotNone(action_execution)
        self.assertEqual(action_executions.ActionExecution(
            self.action_executions, ACTION_EXEC
        ).__dict__, action_execution.__dict__)

        mock.assert_called_once_with(
            URL_TEMPLATE_ID % ACTION_EXEC['id'], json.dumps(body))

    def test_list(self):
        mock = self.mock_http_get(
            content={'action_executions': [ACTION_EXEC]}
        )

        action_execution_list = self.action_executions.list()

        self.assertEqual(1, len(action_execution_list))
        action_execution = action_execution_list[0]

        self.assertEqual(action_executions.ActionExecution(
            self.action_executions, ACTION_EXEC
        ).__dict__, action_execution.__dict__)

        mock.assert_called_once_with(URL_TEMPLATE)

    def test_get(self):
        mock = self.mock_http_get(content=ACTION_EXEC)

        action_execution = self.action_executions.get(ACTION_EXEC['id'])

        self.assertEqual(action_executions.ActionExecution(
            self.action_executions, ACTION_EXEC
        ).__dict__, action_execution.__dict__)

        mock.assert_called_once_with(
            URL_TEMPLATE_ID % ACTION_EXEC['id'])
