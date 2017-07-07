# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
# Copyright 2016 - Brocade Communications Systems, Inc.
#
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

import mock
import pkg_resources as pkg
import six
import sys

from mistralclient.api.v2 import executions
from mistralclient.commands.v2 import executions as execution_cmd
from mistralclient.tests.unit import base

EXEC = executions.Execution(
    mock,
    {
        'id': '123',
        'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
        'workflow_name': 'some',
        'description': '',
        'state': 'RUNNING',
        'state_info': None,
        'created_at': '1',
        'updated_at': '1',
        'task_execution_id': None
    }
)

SUB_WF_EXEC = executions.Execution(
    mock,
    {
        'id': '456',
        'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
        'workflow_name': 'some_sub_wf',
        'description': '',
        'state': 'RUNNING',
        'state_info': None,
        'created_at': '1',
        'updated_at': '1',
        'task_execution_id': 'abc'
    }
)

EX_RESULT = (
    '123',
    '123e4567-e89b-12d3-a456-426655440000',
    'some',
    '',
    '<none>',
    'RUNNING',
    None,
    '1',
    '1'
)

SUB_WF_EX_RESULT = (
    '456',
    '123e4567-e89b-12d3-a456-426655440000',
    'some_sub_wf',
    '',
    'abc',
    'RUNNING',
    None,
    '1',
    '1'
)


class TestCLIExecutionsV2(base.BaseCommandTest):

    stdout = six.moves.StringIO()
    stderr = six.moves.StringIO()

    def setUp(self):
        super(TestCLIExecutionsV2, self).setUp()

        # Redirect stdout and stderr so it doesn't pollute the test result.
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def tearDown(self):
        super(TestCLIExecutionsV2, self).tearDown()

        # Reset to original stdout and stderr.
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def test_create_wf_input_string(self):
        self.client.executions.create.return_value = EXEC

        result = self.call(
            execution_cmd.Create,
            app_args=['id', '{ "context": true }']
        )

        self.assertEqual(
            EX_RESULT,
            result[1]
        )

    def test_create_wf_input_file(self):
        self.client.executions.create.return_value = EXEC

        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/ctx.json'
        )

        result = self.call(
            execution_cmd.Create,
            app_args=['id', path]
        )

        self.assertEqual(
            EX_RESULT,
            result[1]
        )

    def test_create_with_description(self):
        self.client.executions.create.return_value = EXEC

        result = self.call(
            execution_cmd.Create,
            app_args=['id', '{ "context": true }', '-d', '']
        )

        self.assertEqual(
            EX_RESULT,
            result[1]
        )

    def test_update_state(self):
        states = ['RUNNING', 'SUCCESS', 'PAUSED', 'ERROR', 'CANCELLED']

        for state in states:
            self.client.executions.update.return_value = executions.Execution(
                mock,
                {
                    'id': '123',
                    'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
                    'workflow_name': 'some',
                    'description': '',
                    'state': state,
                    'state_info': None,
                    'created_at': '1',
                    'updated_at': '1',
                    'task_execution_id': None
                }
            )

            ex_result = list(EX_RESULT)
            ex_result[5] = state
            ex_result = tuple(ex_result)

            result = self.call(
                execution_cmd.Update,
                app_args=['id', '-s', state]
            )

            self.assertEqual(
                ex_result,
                result[1]
            )

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

        self.assertEqual(
            EX_RESULT,
            result[1]
        )

    def test_update_description(self):
        self.client.executions.update.return_value = EXEC

        result = self.call(
            execution_cmd.Update,
            app_args=['id', '-d', 'foobar']
        )

        self.assertEqual(
            EX_RESULT,
            result[1]
        )

    def test_list(self):
        self.client.executions.list.return_value = [EXEC, SUB_WF_EXEC]

        result = self.call(execution_cmd.List)

        self.assertEqual(
            [EX_RESULT, SUB_WF_EX_RESULT],
            result[1]
        )

    def test_list_with_pagination(self):
        self.client.executions.list.return_value = [EXEC]

        self.call(execution_cmd.List)
        self.client.executions.list.assert_called_once_with(
            limit=100,
            marker='',
            sort_dirs='asc',
            sort_keys='created_at',
            task=None
        )

        self.call(
            execution_cmd.List,
            app_args=[
                '--limit', '5',
                '--sort_dirs', 'id, Workflow',
                '--sort_keys', 'desc',
                '--marker', 'abc'
            ]
        )

        self.client.executions.list.assert_called_with(
            limit=5,
            marker='abc',
            sort_dirs='id, Workflow',
            sort_keys='desc',
            task=None
        )

    def test_get(self):
        self.client.executions.get.return_value = EXEC

        result = self.call(execution_cmd.Get, app_args=['id'])

        self.assertEqual(
            EX_RESULT,
            result[1]
        )

    def test_get_sub_wf_ex(self):
        self.client.executions.get.return_value = SUB_WF_EXEC

        result = self.call(execution_cmd.Get, app_args=['id'])

        self.assertEqual(
            SUB_WF_EX_RESULT,
            result[1]
        )

    def test_delete(self):
        self.call(execution_cmd.Delete, app_args=['id'])

        self.client.executions.delete.assert_called_once_with('id')

    def test_delete_with_multi_names(self):
        self.call(execution_cmd.Delete, app_args=['id1', 'id2'])

        self.assertEqual(2, self.client.executions.delete.call_count)
        self.assertEqual(
            [mock.call('id1'), mock.call('id2')],
            self.client.executions.delete.call_args_list
        )
