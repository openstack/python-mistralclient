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

import unittest2
import json

from mistralclient.tests import base
from mistralclient.api.executions import Execution

# TODO: Later we need additional tests verifying all the errors etc.

EXECS = [
    {
        'id': "123",
        'workbook_name': "my_workbook",
        'task': 'my_task',
        'state': 'RUNNING',
        'context': """
            {
                "person": {
                    "first_name": "John",
                    "last_name": "Doe"
                }
            }
        """
    }
]

URL_TEMPLATE = '/workbooks/%s/executions'
URL_TEMPLATE_ID = '/workbooks/%s/executions/%s'


class TestExecutions(base.BaseClientTest):
    def test_create(self):
        mock = self.mock_http_post(content=EXECS[0])
        body = {
            'task': EXECS[0]['task'],
            'context': EXECS[0]['context'],
            'workbook_name': EXECS[0]['workbook_name']
        }

        ex = self.executions.create(EXECS[0]['workbook_name'],
                                    EXECS[0]['task'],
                                    EXECS[0]['context'])

        self.assertIsNotNone(ex)
        self.assertEqual(Execution(self.executions, EXECS[0]).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE % EXECS[0]['workbook_name'],
            json.dumps(body))

    def test_create_with_empty_context(self):
        mock = self.mock_http_post(content=EXECS[0])
        body = {
            'task': EXECS[0]['task'],
            'workbook_name': EXECS[0]['workbook_name']
        }

        self.executions.create(EXECS[0]['workbook_name'],
                               EXECS[0]['task'])

        mock.assert_called_once_with(
            URL_TEMPLATE % EXECS[0]['workbook_name'],
            json.dumps(body))

    @unittest2.expectedFailure
    def test_create_failure1(self):
        self.mock_http_post(content=EXECS[0])
        self.executions.create(EXECS[0]['workbook_name'],
                               EXECS[0]['task'],
                               "sdfsdf")

    @unittest2.expectedFailure
    def test_create_failure2(self):
        self.mock_http_post(content=EXECS[0])
        self.executions.create(EXECS[0]['workbook_name'],
                               EXECS[0]['task'],
                               list('343', 'sdfsd'))

    def test_update(self):
        mock = self.mock_http_put(content=EXECS[0])
        body = {
            'state': EXECS[0]['state']
        }

        ex = self.executions.update(EXECS[0]['workbook_name'],
                                    EXECS[0]['id'],
                                    EXECS[0]['state'])

        self.assertIsNotNone(ex)
        self.assertEqual(Execution(self.executions, EXECS[0]).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (EXECS[0]['workbook_name'], EXECS[0]['id']),
            json.dumps(body))

    def test_list(self):
        mock = self.mock_http_get(content={'executions': EXECS})

        executions = self.executions.list(EXECS[0]['workbook_name'])

        self.assertEqual(1, len(executions))
        ex = executions[0]

        self.assertEqual(Execution(self.executions, EXECS[0]).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(URL_TEMPLATE % EXECS[0]['workbook_name'])

    def test_get(self):
        mock = self.mock_http_get(content=EXECS[0])

        ex = self.executions.get(EXECS[0]['workbook_name'], EXECS[0]['id'])

        self.assertEqual(Execution(self.executions, EXECS[0]).__dict__,
                         ex.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (EXECS[0]['workbook_name'], EXECS[0]['id']))

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.executions.delete(EXECS[0]['workbook_name'], EXECS[0]['id'])

        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (EXECS[0]['workbook_name'], EXECS[0]['id']))
