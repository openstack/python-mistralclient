# Copyright 2014 - Mirantis, Inc.
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

import unittest2

from mistralclient.api.v2 import executions
from mistralclient.tests.unit.v2 import base

# TODO(everyone): Later we need additional tests verifying all the errors etc.

EXEC = {
    'id': "123",
    'workflow_name': 'my_wf',
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
        mock = self.mock_http_post(content=EXEC)
        body = {
            'workflow_name': EXEC['workflow_name'],
            'description': '',
            'input': json.dumps(EXEC['input']),
        }

        ex = self.executions.create(EXEC['workflow_name'],
                                    EXEC['input'])

        self.assertIsNotNone(ex)
        self.assertEqual(executions.Execution(self.executions, EXEC).to_dict(),
                         ex.to_dict())
        mock.assert_called_once_with(URL_TEMPLATE, json.dumps(body))

    @unittest2.expectedFailure
    def test_create_failure1(self):
        self.mock_http_post(content=EXEC)
        self.executions.create("")

    @unittest2.expectedFailure
    def test_create_failure2(self):
        self.mock_http_post(content=EXEC)
        self.executions.create(EXEC['workflow_name'],
                               list('343', 'sdfsd'))

    def test_update(self):
        mock = self.mock_http_put(content=EXEC)
        body = {
            'state': EXEC['state']
        }

        ex = self.executions.update(EXEC['id'], EXEC['state'])

        self.assertIsNotNone(ex)
        self.assertEqual(executions.Execution(self.executions, EXEC).to_dict(),
                         ex.to_dict())
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % EXEC['id'], json.dumps(body))

    def test_list(self):
        mock = self.mock_http_get(content={'executions': [EXEC]})

        execution_list = self.executions.list()

        self.assertEqual(1, len(execution_list))
        ex = execution_list[0]

        self.assertEqual(executions.Execution(self.executions, EXEC).to_dict(),
                         ex.to_dict())
        mock.assert_called_once_with(URL_TEMPLATE)

    def test_list_with_pagination(self):
        mock = self.mock_http_get(
            content={'executions': [EXEC], 'next': '/executions?fake'}
        )

        execution_list = self.executions.list(
            limit=1,
            sort_keys='created_at',
            sort_dirs='asc'
        )

        self.assertEqual(1, len(execution_list))

        # The url param order is unpredictable.
        self.assertIn('limit=1', mock.call_args[0][0])
        self.assertIn('sort_keys=created_at', mock.call_args[0][0])
        self.assertIn('sort_dirs=asc', mock.call_args[0][0])

    def test_get(self):
        mock = self.mock_http_get(content=EXEC)

        ex = self.executions.get(EXEC['id'])

        self.assertEqual(executions.Execution(self.executions, EXEC).to_dict(),
                         ex.to_dict())
        mock.assert_called_once_with(URL_TEMPLATE_ID % EXEC['id'])

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.executions.delete(EXEC['id'])

        mock.assert_called_once_with(URL_TEMPLATE_ID % EXEC['id'])
