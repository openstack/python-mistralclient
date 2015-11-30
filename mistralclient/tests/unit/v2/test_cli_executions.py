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

import mock
import pkg_resources as pkg

from mistralclient.api.v2 import executions
from mistralclient.commands.v2 import executions as execution_cmd
from mistralclient.tests.unit import base

EXECUTION = executions.Execution(mock, {
    'id': '123',
    'workflow_name': 'some',
    'description': '',
    'state': 'RUNNING',
    'state_info': None,
    'created_at': '1',
    'updated_at': '1'
})


class TestCLIExecutionsV2(base.BaseCommandTest):
    def test_create_wf_input_string(self):
        self.client.executions.create.return_value = EXECUTION

        result = self.call(execution_cmd.Create,
                           app_args=['id', '{ "context": true }'])

        self.assertEqual(('123', 'some', '', 'RUNNING', None,
                          '1', '1'), result[1])

    def test_create_wf_input_file(self):
        self.client.executions.create.return_value = EXECUTION
        path = pkg.resource_filename('mistralclient',
                                     'tests/unit/resources/ctx.json')
        result = self.call(execution_cmd.Create,
                           app_args=['id', path])

        self.assertEqual(('123', 'some', '', 'RUNNING', None,
                          '1', '1'), result[1])

    def test_create_with_description(self):
        self.client.executions.create.return_value = EXECUTION

        result = self.call(execution_cmd.Create,
                           app_args=['id', '{ "context": true }', '-d', ''])

        self.assertEqual(('123', 'some', '', 'RUNNING', None,
                          '1', '1'), result[1])

    def test_update(self):
        self.client.executions.update.return_value = EXECUTION

        result = self.call(execution_cmd.Update,
                           app_args=['id', '-s', 'SUCCESS'])

        self.assertEqual(('123', 'some', '', 'RUNNING', None,
                          '1', '1'), result[1])

    def test_list(self):
        self.client.executions.list.return_value = (EXECUTION,)

        result = self.call(execution_cmd.List)

        self.assertEqual([('123', 'some', '', 'RUNNING', None,
                          '1', '1')], result[1])

    def test_list_with_pagination(self):
        self.client.executions.list.return_value = (EXECUTION,)

        self.call(execution_cmd.List)
        self.client.executions.list.assert_called_once_with(
            limit=None,
            marker='',
            sort_dirs='asc',
            sort_keys='created_at'
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
            sort_keys='desc'
        )

    def test_get(self):
        self.client.executions.get.return_value = EXECUTION

        result = self.call(execution_cmd.Get, app_args=['id'])

        self.assertEqual(('123', 'some', '', 'RUNNING', None,
                          '1', '1'), result[1])

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
