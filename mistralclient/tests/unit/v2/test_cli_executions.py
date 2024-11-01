# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
# Copyright 2016 - Brocade Communications Systems, Inc.
# Copyright 2020 - Nokia Software.
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

import os.path
from unittest import mock

from oslo_serialization import jsonutils

from mistralclient.api.v2 import executions
from mistralclient.commands.v2 import executions as execution_cmd
from mistralclient.tests.unit import base

EXEC_DICT = {
    'id': '123',
    'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
    'workflow_name': 'some',
    'workflow_namespace': '',
    'root_execution_id': '',
    'description': '',
    'state': 'SUCCESS',
    'state_info': None,
    'created_at': '2020-02-07 08:10:32',
    'updated_at': '2020-02-07 08:10:41',
    'task_execution_id': None
}

EXEC = executions.Execution(mock, EXEC_DICT)

SUB_WF_EXEC = executions.Execution(
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
        'task_execution_id': 'abc'
    }
)

EX_RESULT = (
    '123',
    '123e4567-e89b-12d3-a456-426655440000',
    'some',
    '',
    '',
    '<none>',
    '<none>',
    'SUCCESS',
    None,
    '2020-02-07 08:10:32',
    '2020-02-07 08:10:41',
    '0:00:09'
)

SUB_WF_EX_RESULT = (
    '456',
    '123e4567-e89b-12d3-a456-426655440000',
    'some_sub_wf',
    '',
    '',
    'abc',
    'ROOT_EXECUTION_ID',
    'ERROR',
    None,
    '2020-02-07 08:10:32',
    '2020-02-07 08:10:41',
    '0:00:09'
)

EXECS_LIST = [EXEC, SUB_WF_EXEC]
EXEC_PUBLISHED = {"bar1": "val1", "var2": 2}
EXEC_WITH_PUBLISHED_DICT = EXEC_DICT.copy()
EXEC_WITH_PUBLISHED_DICT.update(
    {'published_global': jsonutils.dumps(EXEC_PUBLISHED)})
EXEC_WITH_PUBLISHED = executions.Execution(mock, EXEC_WITH_PUBLISHED_DICT)


class TestCLIExecutionsV2(base.BaseCommandTest):
    def setUp(self):
        super(TestCLIExecutionsV2, self).setUp()

    def tearDown(self):
        super(TestCLIExecutionsV2, self).tearDown()

    def test_create_wf_input_string(self):
        self.client.executions.create.return_value = EXEC

        result = self.call(
            execution_cmd.Create,
            app_args=['id', '{ "context": true }']
        )

        self.assertEqual(EX_RESULT, result[1])

    def test_create_wf_input_file(self):
        self.client.executions.create.return_value = EXEC

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', 'resources', 'ctx.json')

        result = self.call(
            execution_cmd.Create,
            app_args=['id', path]
        )

        self.assertEqual(EX_RESULT, result[1])

    def test_create_with_description(self):
        self.client.executions.create.return_value = EXEC

        result = self.call(
            execution_cmd.Create,
            app_args=['id', '{ "context": true }', '-d', '']
        )

        self.assertEqual(EX_RESULT, result[1])

    def test_update_state(self):
        states = ['RUNNING', 'SUCCESS', 'PAUSED', 'ERROR', 'CANCELLED']

        for state in states:
            self.client.executions.update.return_value = executions.Execution(
                mock,
                {
                    'id': '123',
                    'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
                    'workflow_name': 'some',
                    'workflow_namespace': '',
                    'root_execution_id': '',
                    'description': '',
                    'state': state,
                    'state_info': None,
                    'created_at': '2020-02-07 08:10:32',
                    'updated_at': '2020-02-07 08:10:41',
                    'task_execution_id': None
                }
            )

            ex_result = list(EX_RESULT)
            ex_result[7] = state

            # We'll ignore "duration" since for not terminal states
            # it is unpredictable.
            del ex_result[11]
            ex_result = tuple(ex_result)

            result = self.call(
                execution_cmd.Update,
                app_args=['id', '-s', state]
            )

            result_ex = list(result[1])
            del result_ex[11]
            result_ex = tuple(result_ex)

            self.assertEqual(ex_result, result_ex)

    def test_update_invalid_state(self):
        states = ['IDLE', 'WAITING', 'DELAYED']

        for state in states:
            self.assertRaises(
                SystemExit,
                self.call,
                execution_cmd.Update,
                app_args=['id', '-s', state]
            )

    def test_resume_update_env(self):
        self.client.executions.update.return_value = EXEC

        result = self.call(
            execution_cmd.Update,
            app_args=['id', '-s', 'RUNNING', '--env', '{"k1": "foobar"}']
        )

        self.assertEqual(EX_RESULT, result[1])

    def test_update_description(self):
        self.client.executions.update.return_value = EXEC

        result = self.call(
            execution_cmd.Update,
            app_args=['id', '-d', 'foobar']
        )

        self.assertEqual(EX_RESULT, result[1])

    def test_list(self):
        self.client.executions.list.return_value = [SUB_WF_EXEC, EXEC]

        result = self.call(execution_cmd.List)

        self.assertEqual(
            [EX_RESULT, SUB_WF_EX_RESULT],
            result[1]
        )

    def test_sub_executions(self):
        self.client.executions.get_ex_sub_executions.return_value = \
            EXECS_LIST

        result = self.call(
            execution_cmd.SubExecutionsLister,
            app_args=[EXEC_DICT['id']]
        )

        self.assertEqual([EX_RESULT, SUB_WF_EX_RESULT], result[1])
        self.assertEqual(
            1,
            self.client.executions.get_ex_sub_executions.call_count
        )
        self.assertEqual(
            [mock.call(EXEC_DICT['id'], errors_only='', max_depth=-1)],
            self.client.executions.get_ex_sub_executions.call_args_list
        )

    def test_sub_executions_errors_only(self):
        self.client.executions.get_ex_sub_executions.return_value = \
            EXECS_LIST

        self.call(
            execution_cmd.SubExecutionsLister,
            app_args=[EXEC_DICT['id'], '--errors-only']
        )

        self.assertEqual(
            1,
            self.client.executions.get_ex_sub_executions.call_count
        )
        self.assertEqual(
            [mock.call(EXEC_DICT['id'], errors_only=True, max_depth=-1)],
            self.client.executions.get_ex_sub_executions.call_args_list
        )

    def test_sub_executions_with_max_depth(self):
        self.client.executions.get_ex_sub_executions.return_value = \
            EXECS_LIST

        self.call(
            execution_cmd.SubExecutionsLister,
            app_args=[EXEC_DICT['id'], '--max-depth', '3']
        )

        self.assertEqual(
            1,
            self.client.executions.get_ex_sub_executions.call_count
        )
        self.assertEqual(
            [mock.call(EXEC_DICT['id'], errors_only='', max_depth=3)],
            self.client.executions.get_ex_sub_executions.call_args_list
        )

    def test_list_with_pagination(self):
        self.client.executions.list.return_value = [EXEC]

        self.call(execution_cmd.List)
        self.client.executions.list.assert_called_once_with(
            fields=execution_cmd.ExecutionFormatter.fields(),
            limit=100,
            marker='',
            nulls='',
            sort_dirs='desc',
            sort_keys='created_at',
            task=None
        )

        self.call(
            execution_cmd.List,
            app_args=[
                '--oldest'
            ]
        )

        self.client.executions.list.assert_called_with(
            fields=execution_cmd.ExecutionFormatter.fields(),
            limit=100,
            marker='',
            nulls='',
            sort_keys='created_at',
            sort_dirs='asc',
            task=None
        )

        self.call(
            execution_cmd.List,
            app_args=[
                '--limit', '5',
                '--sort_keys', 'id, Workflow',
                '--sort_dirs', 'desc',
                '--marker', 'abc'
            ]
        )

        self.client.executions.list.assert_called_with(
            fields=execution_cmd.ExecutionFormatter.fields(),
            limit=5,
            marker='abc',
            nulls='',
            sort_keys='id, Workflow',
            sort_dirs='desc',
            task=None
        )

    def test_get(self):
        self.client.executions.get.return_value = EXEC

        result = self.call(execution_cmd.Get, app_args=['id'])

        self.assertEqual(EX_RESULT, result[1])

    def test_get_sub_wf_ex(self):
        self.client.executions.get.return_value = SUB_WF_EXEC

        result = self.call(execution_cmd.Get, app_args=['id'])

        self.assertEqual(SUB_WF_EX_RESULT, result[1])

    def test_delete(self):
        self.call(execution_cmd.Delete, app_args=['id'])

        self.client.executions.delete.assert_called_once_with(
            'id',
            force=False
        )

    def test_delete_with_force(self):
        self.call(execution_cmd.Delete, app_args=['id', '--force'])

        self.client.executions.delete.assert_called_once_with(
            'id',
            force=True
        )

    def test_delete_with_multi_names(self):
        self.call(execution_cmd.Delete, app_args=['id1', 'id2'])

        self.assertEqual(2, self.client.executions.delete.call_count)
        self.assertEqual(
            [mock.call('id1', force=False), mock.call('id2', force=False)],
            self.client.executions.delete.call_args_list
        )

    def test_get_published(self):
        self.client.executions.get.return_value = EXEC_WITH_PUBLISHED

        self.call(execution_cmd.GetPublished, app_args=['id'])

        self.assertDictEqual(
            EXEC_PUBLISHED,
            jsonutils.loads(self.app.stdout.write.call_args[0][0])
        )
