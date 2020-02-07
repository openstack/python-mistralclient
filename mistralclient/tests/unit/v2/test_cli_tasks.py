# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
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

from oslo_serialization import jsonutils

import mock

from mistralclient.api.v2.executions import Execution
from mistralclient.api.v2 import tasks
from mistralclient.commands.v2 import tasks as task_cmd
from mistralclient.tests.unit import base

TASK_DICT = {
    'id': '123',
    'name': 'some',
    'workflow_name': 'thing',
    'workflow_namespace': '',
    'workflow_execution_id': '321',
    'state': 'SUCCESS',
    'state_info': None,
    'created_at': '2020-02-07 08:10:32',
    'started_at': '2020-02-07 08:10:32',
    'finished_at': '2020-02-07 08:10:41'
}

TASK_SUB_WF_EXEC = Execution(
    mock,
    {
        'id': '456',
        'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
        'workflow_name': 'some_sub_wf',
        'workflow_namespace': '',
        'root_execution_id': 'ROOT_EXECUTION_ID',
        'description': '',
        'state': 'ERROR',
        'state_info': None,
        'created_at': '2020-02-07 08:10:32',
        'updated_at': '2020-02-07 08:10:41',
        'task_execution_id': '123'
    }
)

TASK_SUB_WF_EX_RESULT = (
    '456',
    '123e4567-e89b-12d3-a456-426655440000',
    'some_sub_wf',
    '',
    '',
    '123',
    'ROOT_EXECUTION_ID',
    'ERROR',
    None,
    '2020-02-07 08:10:32',
    '2020-02-07 08:10:41',
    '0:00:09'
)

TASK_RESULT = {"test": "is", "passed": "successfully"}
TASK_PUBLISHED = {"bar1": "val1", "var2": 2}

TASK_WITH_RESULT_DICT = TASK_DICT.copy()
TASK_WITH_RESULT_DICT.update({'result': jsonutils.dumps(TASK_RESULT)})
TASK_WITH_PUBLISHED_DICT = TASK_DICT.copy()
TASK_WITH_PUBLISHED_DICT.update({'published': jsonutils.dumps(TASK_PUBLISHED)})

TASK = tasks.Task(mock, TASK_DICT)
TASK_WITH_RESULT = tasks.Task(mock, TASK_WITH_RESULT_DICT)
TASK_WITH_PUBLISHED = tasks.Task(mock, TASK_WITH_PUBLISHED_DICT)

EXPECTED_TASK_RESULT = (
    '123', 'some', 'thing', '', '321', 'SUCCESS', None,
    '2020-02-07 08:10:32', '2020-02-07 08:10:32',
    '2020-02-07 08:10:41', '0:00:09'
)


class TestCLITasksV2(base.BaseCommandTest):
    def test_list(self):
        self.client.tasks.list.return_value = [TASK]

        result = self.call(task_cmd.List)

        self.assertEqual([EXPECTED_TASK_RESULT], result[1])
        self.assertEqual(
            self.client.tasks.list.call_args[1]["fields"],
            task_cmd.TaskFormatter.fields()
        )

    def test_list_with_workflow_execution(self):
        self.client.tasks.list.return_value = [TASK]

        result = self.call(task_cmd.List, app_args=['workflow_execution'])

        self.assertEqual([EXPECTED_TASK_RESULT], result[1])

    def test_get(self):
        self.client.tasks.get.return_value = TASK

        result = self.call(task_cmd.Get, app_args=['id'])

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    def test_get_result(self):
        self.client.tasks.get.return_value = TASK_WITH_RESULT

        self.call(task_cmd.GetResult, app_args=['id'])

        self.assertDictEqual(
            TASK_RESULT,
            jsonutils.loads(self.app.stdout.write.call_args[0][0])
        )

    def test_get_published(self):
        self.client.tasks.get.return_value = TASK_WITH_PUBLISHED

        self.call(task_cmd.GetPublished, app_args=['id'])

        self.assertDictEqual(
            TASK_PUBLISHED,
            jsonutils.loads(self.app.stdout.write.call_args[0][0])
        )

    def test_rerun(self):
        self.client.tasks.rerun.return_value = TASK

        result = self.call(task_cmd.Rerun, app_args=['id'])

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    def test_rerun_no_reset(self):
        self.client.tasks.rerun.return_value = TASK

        result = self.call(task_cmd.Rerun, app_args=['id', '--resume'])

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    def test_rerun_update_env(self):
        self.client.tasks.rerun.return_value = TASK

        result = self.call(
            task_cmd.Rerun,
            app_args=['id', '--env', '{"k1": "foobar"}']
        )

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    def test_rerun_no_reset_update_env(self):
        self.client.tasks.rerun.return_value = TASK

        result = self.call(
            task_cmd.Rerun,
            app_args=['id', '--resume', '--env', '{"k1": "foobar"}']
        )

        self.assertEqual(EXPECTED_TASK_RESULT, result[1])

    def test_sub_executions(self):
        self.client.tasks.get_task_sub_executions.return_value = \
            TASK_SUB_WF_EXEC

        result = self.call(
            task_cmd.SubExecutionsLister,
            app_args=[TASK_DICT['id']]
        )

        self.assertEqual([TASK_SUB_WF_EX_RESULT], result[1])
        self.assertEqual(
            1,
            self.client.tasks.get_task_sub_executions.call_count
        )
        self.assertEqual(
            [mock.call(TASK_DICT['id'], errors_only='', max_depth=-1)],
            self.client.tasks.get_task_sub_executions.call_args_list
        )

    def test_sub_executions_errors_only(self):
        self.client.tasks.get_task_sub_executions.return_value = \
            TASK_SUB_WF_EXEC

        self.call(
            task_cmd.SubExecutionsLister,
            app_args=[TASK_DICT['id'], '--errors-only']
        )

        self.assertEqual(
            1,
            self.client.tasks.get_task_sub_executions.call_count
        )
        self.assertEqual(
            [mock.call(TASK_DICT['id'], errors_only=True, max_depth=-1)],
            self.client.tasks.get_task_sub_executions.call_args_list
        )

    def test_sub_executions_with_max_depth(self):
        self.client.tasks.get_task_sub_executions.return_value = \
            TASK_SUB_WF_EXEC

        self.call(
            task_cmd.SubExecutionsLister,
            app_args=[TASK_DICT['id'], '--max-depth', '3']
        )

        self.assertEqual(
            1,
            self.client.tasks.get_task_sub_executions.call_count
        )
        self.assertEqual(
            [mock.call(TASK_DICT['id'], errors_only='', max_depth=3)],
            self.client.tasks.get_task_sub_executions.call_args_list
        )
