# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json

from mistralclient.tests import base
from mistralclient.api.tasks import Task

# TODO: later we need additional tests verifying all the errors etc.

TASKS = [
    {
        'id': "1",
        'workbook_name': "my_workbook",
        'execution_id': '123',
        'name': 'my_task',
        'description': 'My cool task',
        'action': 'my_action',
        'state': 'RUNNING',
        'tags': ['deployment', 'demo']
    }
]

URL_TEMPLATE = '/workbooks/%s/executions/%s/tasks'
URL_TEMPLATE_ID = '/workbooks/%s/executions/%s/tasks/%s'


class TestTasks(base.BaseClientTest):
    def test_update(self):
        mock = self.mock_http_put(content=TASKS[0])
        body = {
            'workbook_name': TASKS[0]['workbook_name'],
            'execution_id': TASKS[0]['execution_id'],
            'id': TASKS[0]['id'],
            'state': TASKS[0]['state']
        }

        task = self.tasks.update(TASKS[0]['workbook_name'],
                                 TASKS[0]['execution_id'],
                                 TASKS[0]['id'],
                                 TASKS[0]['state'])

        self.assertIsNotNone(task)
        self.assertEqual(Task(self.tasks, TASKS[0]).__dict__, task.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (TASKS[0]['workbook_name'],
                               TASKS[0]['execution_id'],
                               TASKS[0]['id']),
            json.dumps(body))

    def test_list(self):
        mock = self.mock_http_get(content={'tasks': TASKS})

        tasks = self.tasks.list(TASKS[0]['workbook_name'],
                                TASKS[0]['execution_id'])

        self.assertEqual(1, len(tasks))
        task = tasks[0]

        self.assertEqual(Task(self.tasks, TASKS[0]).__dict__, task.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE % (TASKS[0]['workbook_name'],
                            TASKS[0]['execution_id']))

    def test_get(self):
        mock = self.mock_http_get(content=TASKS[0])

        task = self.tasks.get(TASKS[0]['workbook_name'],
                              TASKS[0]['execution_id'],
                              TASKS[0]['id'])

        self.assertEqual(Task(self.tasks, TASKS[0]).__dict__, task.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (TASKS[0]['workbook_name'],
                               TASKS[0]['execution_id'],
                               TASKS[0]['id']))
