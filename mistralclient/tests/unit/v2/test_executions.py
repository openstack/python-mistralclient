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

from mistralclient.api import base as api_base
from mistralclient.api.v2 import executions
from mistralclient.tests.unit.v2 import base

# TODO(everyone): Later we need additional tests verifying all the errors etc.

EXEC = {
    'id': "123",
    'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
    'workflow_name': 'my_wf',
    'workflow_namespace': '',
    'description': '',
    'state': 'RUNNING',
    'input': {
        "person": {
            "first_name": "John",
            "last_name": "Doe"
        }
    }
}

SUB_WF_EXEC = {
    'id': "456",
    'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
    'workflow_name': 'my_sub_wf',
    'workflow_namespace': '',
    'task_execution_id': "abc",
    'description': '',
    'state': 'RUNNING',
    'input': {
        "person": {
            "first_name": "John",
            "last_name": "Doe"
        }
    }
}

URL_TEMPLATE = '/executions'
URL_TEMPLATE_ID = '/executions/%s'


class TestExecutionsV2(base.BaseClientV2Test):
    def test_create(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE,
                                json=EXEC,
                                status_code=201)

        body = {
            'workflow_name': EXEC['workflow_name'],
            'description': '',
            'input': json.dumps(EXEC['input']),
        }

        ex = self.executions.create(
            EXEC['workflow_name'],
            EXEC['workflow_namespace'],
            EXEC['input']
        )

        self.assertIsNotNone(ex)

        self.assertDictEqual(
            executions.Execution(self.executions, EXEC).to_dict(),
            ex.to_dict()
        )

        self.assertDictEqual(body, self.requests_mock.last_request.json())

    def test_create_with_workflow_id(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE,
                                json=EXEC,
                                status_code=201)

        body = {
            'workflow_id': EXEC['workflow_id'],
            'description': '',
            'input': json.dumps(EXEC['input']),
        }

        ex = self.executions.create(
            EXEC['workflow_id'],
            workflow_input=EXEC['input']
        )

        self.assertIsNotNone(ex)

        self.assertDictEqual(
            executions.Execution(self.executions, EXEC).to_dict(),
            ex.to_dict()
        )

        self.assertDictEqual(body, self.requests_mock.last_request.json())

    def test_create_failure1(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE,
                                json=EXEC,
                                status_code=201)
        self.assertRaises(api_base.APIException, self.executions.create, '')

    def test_update(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % EXEC['id']
        self.requests_mock.put(url, json=EXEC)
        body = {
            'state': EXEC['state']
        }

        ex = self.executions.update(EXEC['id'], EXEC['state'])

        self.assertIsNotNone(ex)

        self.assertDictEqual(
            executions.Execution(self.executions, EXEC).to_dict(),
            ex.to_dict()
        )

        self.assertDictEqual(body, self.requests_mock.last_request.json())

    def test_update_env(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % EXEC['id']
        self.requests_mock.put(url, json=EXEC)
        body = {
            'state': EXEC['state'],
            'params': {
                'env': {'k1': 'foobar'}
            }
        }

        ex = self.executions.update(
            EXEC['id'],
            EXEC['state'],
            env={'k1': 'foobar'}
        )

        self.assertIsNotNone(ex)

        self.assertDictEqual(
            executions.Execution(self.executions, EXEC).to_dict(),
            ex.to_dict()
        )

        self.assertDictEqual(body, self.requests_mock.last_request.json())

    def test_list(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'executions': [EXEC, SUB_WF_EXEC]})

        execution_list = self.executions.list()

        self.assertEqual(2, len(execution_list))

        self.assertDictEqual(
            executions.Execution(self.executions, EXEC).to_dict(),
            execution_list[0].to_dict()
        )

        self.assertDictEqual(
            executions.Execution(self.executions, SUB_WF_EXEC).to_dict(),
            execution_list[1].to_dict()
        )

    def test_list_with_pagination(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'executions': [EXEC],
                                     'next': '/executions?fake'})

        execution_list = self.executions.list(
            limit=1,
            sort_keys='created_at',
            sort_dirs='asc'
        )

        self.assertEqual(1, len(execution_list))

        last_request = self.requests_mock.last_request

        # The url param order is unpredictable.
        self.assertEqual(['1'], last_request.qs['limit'])
        self.assertEqual(['created_at'], last_request.qs['sort_keys'])
        self.assertEqual(['asc'], last_request.qs['sort_dirs'])

    def test_get(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % EXEC['id']
        self.requests_mock.get(url, json=EXEC)

        ex = self.executions.get(EXEC['id'])

        self.assertDictEqual(
            executions.Execution(self.executions, EXEC).to_dict(),
            ex.to_dict()
        )

    def test_get_sub_wf_ex(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % SUB_WF_EXEC['id']
        self.requests_mock.get(url, json=SUB_WF_EXEC)

        ex = self.executions.get(SUB_WF_EXEC['id'])

        self.assertDictEqual(
            executions.Execution(self.executions, SUB_WF_EXEC).to_dict(),
            ex.to_dict()
        )

    def test_delete(self):
        url = self.TEST_URL + URL_TEMPLATE_ID % EXEC['id']
        self.requests_mock.delete(url, status_code=204)

        self.executions.delete(EXEC['id'])
