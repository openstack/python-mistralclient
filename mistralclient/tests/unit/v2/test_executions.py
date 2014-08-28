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

import unittest2
import json

from mistralclient.tests.unit.v2 import base
from mistralclient.api.v2 import executions

# TODO: Later we need additional tests verifying all the errors etc.

EXEC = {
    'id': "123",
    'workflow_name': 'my_wf',
    'state': 'RUNNING',
    'workflow_input': """
        {
            "person": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    """
}


URL_TEMPLATE = '/executions'
URL_TEMPLATE_ID = '/executions/%s'


class TestExecutionsV2(base.BaseClientV2Test):
    def test_create(self):
        mock = self.mock_http_post(content=EXEC)
        body = {
            'workflow_name': EXEC['workflow_name'],
            'workflow_input': EXEC['workflow_input'],
        }

        ex = self.executions.create(EXEC['workflow_name'],
                                    EXEC['workflow_input'])

        self.assertIsNotNone(ex)
        self.assertEqual(executions.Execution(self.executions, EXEC).__dict__,
                         ex.__dict__)
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
        self.assertEqual(executions.Execution(self.executions, EXEC).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % EXEC['id'], json.dumps(body))

    def test_list(self):
        mock = self.mock_http_get(content={'executions': [EXEC]})

        execution_list = self.executions.list()

        self.assertEqual(1, len(execution_list))
        ex = execution_list[0]

        self.assertEqual(executions.Execution(self.executions, EXEC).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(URL_TEMPLATE)

    def test_get(self):
        mock = self.mock_http_get(content=EXEC)

        ex = self.executions.get(EXEC['id'])

        self.assertEqual(executions.Execution(self.executions, EXEC).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(URL_TEMPLATE_ID % EXEC['id'])

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.executions.delete(EXEC['id'])

        mock.assert_called_once_with(URL_TEMPLATE_ID % EXEC['id'])
