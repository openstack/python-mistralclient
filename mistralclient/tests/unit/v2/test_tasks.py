# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
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

from mistralclient.api.v2 import tasks
from mistralclient.tests.unit.v2 import base

# TODO(everyone): later we need additional tests verifying all the errors etc.

TASK = {
    'id': "1",
    'workflow_execution_id': '123',
    'name': 'my_task',
    'workflow_name': 'my_wf',
    'state': 'RUNNING',
    'tags': ['deployment', 'demo'],
    'result': {'some': 'result'}
}


URL_TEMPLATE = '/tasks'
URL_TEMPLATE_ID = '/tasks/%s'


class TestTasksV2(base.BaseClientV2Test):
    def test_list(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'tasks': [TASK]})

        task_list = self.tasks.list()

        self.assertEqual(1, len(task_list))
        task = task_list[0]

        self.assertEqual(
            tasks.Task(self.tasks, TASK).to_dict(),
            task.to_dict()
        )

    def test_get(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % TASK['id']
        self.requests_mock.get(url, json=TASK)

        task = self.tasks.get(TASK['id'])

        self.assertEqual(
            tasks.Task(self.tasks, TASK).to_dict(),
            task.to_dict()
        )

    def test_rerun(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % TASK['id']
        self.requests_mock.put(url, json=TASK)

        task = self.tasks.rerun(TASK['id'])

        self.assertDictEqual(
            tasks.Task(self.tasks, TASK).to_dict(),
            task.to_dict()
        )

        body = {
            'reset': True,
            'state': 'RUNNING',
            'id': TASK['id']
        }
        self.assertDictEqual(body, self.requests_mock.last_request.json())

    def test_rerun_no_reset(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % TASK['id']
        self.requests_mock.put(url, json=TASK)

        task = self.tasks.rerun(TASK['id'], reset=False)

        self.assertDictEqual(
            tasks.Task(self.tasks, TASK).to_dict(),
            task.to_dict()
        )

        body = {
            'reset': False,
            'state': 'RUNNING',
            'id': TASK['id']
        }
        self.assertDictEqual(body, self.requests_mock.last_request.json())

    def test_rerun_update_env(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % TASK['id']
        self.requests_mock.put(url, json=TASK)

        task = self.tasks.rerun(TASK['id'], env={'k1': 'foobar'})

        self.assertDictEqual(
            tasks.Task(self.tasks, TASK).to_dict(),
            task.to_dict()
        )

        body = {
            'reset': True,
            'state': 'RUNNING',
            'id': TASK['id'],
            'env': json.dumps({'k1': 'foobar'})
        }
        self.assertDictEqual(body, self.requests_mock.last_request.json())
