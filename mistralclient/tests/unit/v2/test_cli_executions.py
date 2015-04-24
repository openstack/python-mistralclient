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
    'state': 'RUNNING',
    'state_info': None,
    'created_at': '1',
    'updated_at': '1'
})


class TestCLIExecutionsV2(base.BaseCommandTest):
    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.create')
    def test_create_wf_input_string(self, mock):
        mock.return_value = EXECUTION

        result = self.call(execution_cmd.Create,
                           app_args=['id', '{ "context": true }'])

        self.assertEqual(('123', 'some', 'RUNNING', None,
                          '1', '1'), result[1])

    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.create')
    def test_create_wf_input_file(self, mock):
        mock.return_value = EXECUTION
        path = pkg.resource_filename('mistralclient',
                                     'tests/unit/resources/ctx.json')
        result = self.call(execution_cmd.Create,
                           app_args=['id', path])

        self.assertEqual(('123', 'some', 'RUNNING', None,
                          '1', '1'), result[1])

    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.update')
    def test_update(self, mock):
        mock.return_value = EXECUTION

        result = self.call(execution_cmd.Update,
                           app_args=['id', 'SUCCESS'])

        self.assertEqual(('123', 'some', 'RUNNING', None,
                          '1', '1'), result[1])

    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.list')
    def test_list(self, mock):
        mock.return_value = (EXECUTION,)

        result = self.call(execution_cmd.List)

        self.assertEqual([('123', 'some', 'RUNNING', None,
                          '1', '1')], result[1])

    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.get')
    def test_get(self, mock):
        mock.return_value = EXECUTION

        result = self.call(execution_cmd.Get, app_args=['id'])

        self.assertEqual(('123', 'some', 'RUNNING', None,
                          '1', '1'), result[1])

    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.delete')
    def test_delete(self, del_mock):
        self.call(execution_cmd.Delete, app_args=['id'])

        del_mock.assert_called_once_with('id')

    @mock.patch('mistralclient.api.v2.executions.ExecutionManager.delete')
    def test_delete_with_multi_names(self, del_mock):
        self.call(execution_cmd.Delete, app_args=['id1', 'id2'])

        self.assertEqual(2, del_mock.call_count)
        self.assertEqual(
            [mock.call('id1'), mock.call('id2')],
            del_mock.call_args_list
        )
