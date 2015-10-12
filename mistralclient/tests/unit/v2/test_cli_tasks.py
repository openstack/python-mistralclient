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
    'state_info': None
}

TASK_RESULT = {"test": "is", "passed": "successfully"}
TASK_PUBLISHED = {"bar1": "val1", "var2": 2}

TASK_WITH_RESULT_DICT = TASK_DICT.copy()
TASK_WITH_RESULT_DICT.update({'result': json.dumps(TASK_RESULT)})
TASK_WITH_PUBLISHED_DICT = TASK_DICT.copy()
TASK_WITH_PUBLISHED_DICT.update({'published': json.dumps(TASK_PUBLISHED)})

TASK = tasks.Task(mock, TASK_DICT)
TASK_WITH_RESULT = tasks.Task(mock, TASK_WITH_RESULT_DICT)
TASK_WITH_PUBLISHED = tasks.Task(mock, TASK_WITH_PUBLISHED_DICT)

EXPECTED_TASK_RESULT = ('123', 'some', 'thing', '321', 'RUNNING', None)


class TestCLITasksV2(base.BaseCommandTest):
    @mock.patch('mistralclient.api.v2.tasks.TaskManager.list')
    def test_list(self, mock):
        mock.return_value = (TASK,)

        result = self.call(task_cmd.List)

        self.assertEqual([EXPECTED_TASK_RESULT], result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.list')
    def test_list_with_workflow_execution(self, mock):
        mock.return_value = (TASK,)

        result = self.call(task_cmd.List, app_args=['workflow_execution'])

        self.assertEqual([EXPECTED_TASK_RESULT], result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Get, app_args=['id'])

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get_result(self, mock):
        mock.return_value = TASK_WITH_RESULT

        self.call(task_cmd.GetResult, app_args=['id'])

        self.assertDictEqual(
            TASK_RESULT,
            json.loads(self.app.stdout.write.call_args[0][0])
        )

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get_published(self, mock):
        mock.return_value = TASK_WITH_PUBLISHED

        self.call(task_cmd.GetPublished, app_args=['id'])

        self.assertDictEqual(
            TASK_PUBLISHED,
            json.loads(self.app.stdout.write.call_args[0][0])
        )

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.rerun')
    def test_rerun(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Rerun, app_args=['id'])

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.rerun')
    def test_rerun_no_reset(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Rerun, app_args=['id', '--resume'])

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])
