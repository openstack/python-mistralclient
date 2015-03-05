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

from mistralclient.api.v2 import tasks
from mistralclient.commands.v2 import tasks as task_cmd
from mistralclient.tests.unit import base

TASK_DICT = {
    'id': '123',
    'name': 'some',
    'workflow_name': 'thing',
    'workflow_execution_id': '321',
    'state': 'RUNNING',
}

TASK_RESULT = {"test": "is", "passed": "successfully"}
TASK_INPUT = {"param1": "val1", "param2": 2}

TASK_WITH_RESULT_DICT = TASK_DICT.copy()
TASK_WITH_RESULT_DICT.update({'result': json.dumps(TASK_RESULT)})
TASK_WITH_INPUT_DICT = TASK_DICT.copy()
TASK_WITH_INPUT_DICT.update({'input': json.dumps(TASK_INPUT)})

TASK = tasks.Task(mock, TASK_DICT)
TASK_WITH_RESULT = tasks.Task(mock, TASK_WITH_RESULT_DICT)
TASK_WITH_INPUT = tasks.Task(mock, TASK_WITH_INPUT_DICT)


class TestCLIT1asksV2(base.BaseCommandTest):
    @mock.patch('mistralclient.api.v2.tasks.TaskManager.update')
    def test_update(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Update,
                           app_args=['id', 'ERROR'])

        self.assertEqual(('123', 'some', 'thing', '321', 'RUNNING'),
                         result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.list')
    def test_list(self, mock):
        mock.return_value = (TASK,)

        result = self.call(task_cmd.List)

        self.assertEqual([('123', 'some', 'thing', '321', 'RUNNING')],
                         result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Get, app_args=['id'])

        self.assertEqual(('123', 'some', 'thing', '321', 'RUNNING'),
                         result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get_result(self, mock):
        mock.return_value = TASK_WITH_RESULT

        self.call(task_cmd.GetResult, app_args=['id'])

        self.app.stdout.write.assert_called_with(
            json.dumps(TASK_RESULT, indent=4) + "\n")

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get_input(self, mock):
        mock.return_value = TASK_WITH_INPUT

        self.call(task_cmd.GetInput, app_args=['id'])

        self.app.stdout.write.assert_called_with(
            json.dumps(TASK_INPUT, indent=4) + "\n"
        )
