# Copyright 2014 Mirantis, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import json

import mock

from mistralclient.api.v2 import action_executions as action_ex
from mistralclient.commands.v2 import action_executions as action_ex_cmd
from mistralclient.tests.unit import base

ACTION_EX_DICT = {
    'id': '123',
    'name': 'some',
    'workflow_name': 'thing',
    'task_name': 'task1',
    'state': 'RUNNING',
    'state_info': 'RUNNING somehow.',
    'accepted': True
}

ACTION_EX_RESULT = {"test": "is", "passed": "successfully"}
ACTION_EX_INPUT = {"param1": "val1", "param2": 2}

ACTION_EX_WITH_OUTPUT_DICT = ACTION_EX_DICT.copy()
ACTION_EX_WITH_OUTPUT_DICT.update({'output': json.dumps(ACTION_EX_RESULT)})
ACTION_EX_WITH_INPUT_DICT = ACTION_EX_DICT.copy()
ACTION_EX_WITH_INPUT_DICT.update({'input': json.dumps(ACTION_EX_INPUT)})

ACTION_EX = action_ex.ActionExecution(mock, ACTION_EX_DICT)
ACTION_EX_WITH_OUTPUT = action_ex.ActionExecution(
    mock, ACTION_EX_WITH_OUTPUT_DICT
)
ACTION_EX_WITH_INPUT = action_ex.ActionExecution(
    mock, ACTION_EX_WITH_INPUT_DICT
)


class TestCLIActionExecutions(base.BaseCommandTest):
    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.create'
    )
    def test_create(self, mock):
        mock.return_value = ACTION_EX_WITH_OUTPUT

        self.call(
            action_ex_cmd.Create,
            app_args=['some', '{"output": "Hello!"}']
        )

        self.app.stdout.write.assert_called_with(
            json.dumps(ACTION_EX_RESULT) + "\n")

    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.create'
    )
    def test_create_save_result(self, mock):
        mock.return_value = ACTION_EX_WITH_OUTPUT

        result = self.call(
            action_ex_cmd.Create,
            app_args=[
                'some', '{"output": "Hello!"}', '--save-result'
            ]
        )

        self.assertEqual(
            ('123', 'some', 'thing', 'task1', 'RUNNING',
             'RUNNING somehow.', True), result[1]
        )

    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.update'
    )
    def test_update(self, mock):
        mock.return_value = ACTION_EX

        result = self.call(action_ex_cmd.Update,
                           app_args=['id', '--state', 'ERROR'])

        self.assertEqual(
            ('123', 'some', 'thing', 'task1', 'RUNNING',
             'RUNNING somehow.', True), result[1]
        )

    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.list'
    )
    def test_list(self, mock):
        mock.return_value = (ACTION_EX,)

        result = self.call(action_ex_cmd.List)

        self.assertEqual(
            [('123', 'some', 'thing', 'task1', 'RUNNING',
              'RUNNING somehow.', True)], result[1]
        )

    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.get'
    )
    def test_get(self, mock):
        mock.return_value = ACTION_EX

        result = self.call(action_ex_cmd.Get, app_args=['id'])

        self.assertEqual(
            ('123', 'some', 'thing', 'task1', 'RUNNING',
             'RUNNING somehow.', True), result[1]
        )

    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.get'
    )
    def test_get_output(self, mock):
        mock.return_value = ACTION_EX_WITH_OUTPUT

        self.call(action_ex_cmd.GetOutput, app_args=['id'])

        self.app.stdout.write.assert_called_with(
            json.dumps(ACTION_EX_RESULT, indent=4) + "\n")

    @mock.patch(
        'mistralclient.api.v2.action_executions.ActionExecutionManager.get'
    )
    def test_get_input(self, mock):
        mock.return_value = ACTION_EX_WITH_INPUT

        self.call(action_ex_cmd.GetInput, app_args=['id'])

        self.app.stdout.write.assert_called_with(
            json.dumps(ACTION_EX_INPUT, indent=4) + "\n"
        )
