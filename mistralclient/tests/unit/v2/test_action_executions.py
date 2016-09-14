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
    def test_create(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE,
                                json=ACTION_EXEC,
                                status_code=201)

        body = {
            'name': ACTION_EXEC['name']
        }

        action_execution = self.action_executions.create(
            'my_action_execution',
            {}
        )

        self.assertIsNotNone(action_execution)
        self.assertEqual(action_executions.ActionExecution(
            self.action_executions, ACTION_EXEC
        ).to_dict(), action_execution.to_dict())

        self.assertEqual(body, self.requests_mock.last_request.json())

    def test_update(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % ACTION_EXEC['id']
        self.requests_mock.put(url, json=ACTION_EXEC)

        body = {
            'state': ACTION_EXEC['state']
        }

        action_execution = self.action_executions.update(
            ACTION_EXEC['id'],
            ACTION_EXEC['state']
        )

        self.assertIsNotNone(action_execution)

        expected = action_executions.ActionExecution(
            self.action_executions,
            ACTION_EXEC
        ).to_dict()

        self.assertEqual(
            expected,
            action_execution.to_dict()
        )

        self.assertEqual(body, self.requests_mock.last_request.json())

    def test_list(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'action_executions': [ACTION_EXEC]})

        action_execution_list = self.action_executions.list()

        self.assertEqual(1, len(action_execution_list))
        action_execution = action_execution_list[0]

        expected = action_executions.ActionExecution(
            self.action_executions,
            ACTION_EXEC
        ).to_dict()

        self.assertEqual(expected, action_execution.to_dict())

    def test_get(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % ACTION_EXEC['id']
        self.requests_mock.get(url, json=ACTION_EXEC)

        action_execution = self.action_executions.get(ACTION_EXEC['id'])

        expected = action_executions.ActionExecution(
            self.action_executions,
            ACTION_EXEC
        ).to_dict()

        self.assertEqual(expected, action_execution.to_dict())

    def test_delete(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % ACTION_EXEC['id']
        self.requests_mock.delete(url, status_code=204)

        self.action_executions.delete(ACTION_EXEC['id'])
