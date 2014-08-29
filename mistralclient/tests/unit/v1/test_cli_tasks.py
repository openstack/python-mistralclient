# Copyright 2014 StackStorm, Inc.
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

from mistralclient.commands.v1 import tasks
from mistralclient.api.v1.tasks import Task

TASK = Task(mock, {
    'id': '123',
    'workbook_name': 'some',
    'execution_id': 'thing',
    'name': 'else',
    'description': 'keeps',
    'state': 'RUNNING',
    'tags': ['a', 'b'],
})


class TestCLIExecutions(base.BaseCommandTest):
    @mock.patch('mistralclient.api.v1.tasks.TaskManager.update')
    def test_update(self, mock):
        mock.return_value = TASK

        result = self.call(tasks.Update,
                           app_args=['workbook', 'executor', 'id', 'ERROR'])

        self.assertEqual(
            ('123', 'some', 'thing', 'else', 'keeps', 'RUNNING', 'a, b'),
            result[1])

    @mock.patch('mistralclient.api.v1.tasks.TaskManager.list')
    def test_list(self, mock):
        mock.return_value = (TASK,)

        result = self.call(tasks.List, app_args=['workbook', 'executor'])

        self.assertEqual(
            [('123', 'some', 'thing', 'else', 'keeps', 'RUNNING', 'a, b')],
            result[1])

    @mock.patch('mistralclient.api.v1.tasks.TaskManager.get')
    def test_get(self, mock):
        mock.return_value = TASK

        result = self.call(tasks.Get, app_args=['workbook', 'executor', 'id'])

        self.assertEqual(
            ('123', 'some', 'thing', 'else', 'keeps', 'RUNNING', 'a, b'),
            result[1])
