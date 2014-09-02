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

from mistralclient.tests.unit import base

from mistralclient.commands.v2 import tasks as task_cmd
from mistralclient.api.v2 import tasks

TASK = tasks.Task(mock, {
    'id': '123',
    'name': 'some',
    'wf_name': 'thing',
    'execution_id': '321',
    'state': 'RUNNING',
    'parameters': {},
})


class TestCLIT1asksV2(base.BaseCommandTest):
    @mock.patch('mistralclient.api.v2.tasks.TaskManager.update')
    def test_update(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Update,
                           app_args=['id', 'ERROR'])

        self.assertEqual(('123', 'some', 'thing', '321', 'RUNNING', {}),
                         result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.list')
    def test_list(self, mock):
        mock.return_value = (TASK,)

        result = self.call(task_cmd.List)

        self.assertEqual([('123', 'some', 'thing', '321', 'RUNNING', {})],
                         result[1])

    @mock.patch('mistralclient.api.v2.tasks.TaskManager.get')
    def test_get(self, mock):
        mock.return_value = TASK

        result = self.call(task_cmd.Get, app_args=['id'])

        self.assertEqual(('123', 'some', 'thing', '321', 'RUNNING', {}),
                         result[1])
