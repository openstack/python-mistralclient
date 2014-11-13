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

from mistralclient.api.v1 import workbooks as w
from mistralclient.tests.unit.v1 import base

# TODO(everyone): later we need additional tests verifying all the errors etc.

WORKBOOKS = [
    {
        'name': "my_workbook",
        'description': "My cool Mistral workbook",
        'tags': ['deployment', 'demo']
    }
]

WB_DEF = """
Service:
   name: my_service
   type: REST
   parameters:
       baseUrl: http://my.service.org
   actions:
       action1:
         parameters:
             url: servers
             method: POST
         task-parameters:
            param1:
              optional: false
            param2:
              optional: false
Workflow:
   tasks:
     task1:
         action: my_service:create-vm
         parameters:
            param1: 1234
            param2: 42
"""

URL_TEMPLATE = '/workbooks'
URL_TEMPLATE_NAME = '/workbooks/%s'
URL_TEMPLATE_DEFINITION = '/workbooks/%s/definition'


class TestWorkbooks(base.BaseClientV1Test):
    def test_create(self):
        mock = self.mock_http_post(content=WORKBOOKS[0])

        wb = self.workbooks.create(WORKBOOKS[0]['name'],
                                   WORKBOOKS[0]['description'],
                                   WORKBOOKS[0]['tags'])

        self.assertIsNotNone(wb)
        self.assertEqual(w.Workbook(self.workbooks, WORKBOOKS[0]).__dict__,
                         wb.__dict__)
        mock.assert_called_once_with(URL_TEMPLATE, json.dumps(WORKBOOKS[0]))

    def test_update(self):
        mock = self.mock_http_put(content=WORKBOOKS[0])

        wb = self.workbooks.update(WORKBOOKS[0]['name'],
                                   WORKBOOKS[0]['description'],
                                   WORKBOOKS[0]['tags'])

        self.assertIsNotNone(wb)
        self.assertEqual(w.Workbook(self.workbooks, WORKBOOKS[0]).__dict__,
                         wb.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_NAME % WORKBOOKS[0]['name'],
            json.dumps(WORKBOOKS[0]))

    def test_list(self):
        mock = self.mock_http_get(content={'workbooks': WORKBOOKS})

        workbooks = self.workbooks.list()

        self.assertEqual(1, len(workbooks))
        wb = workbooks[0]

        self.assertEqual(w.Workbook(self.workbooks, WORKBOOKS[0]).__dict__,
                         wb.__dict__)
        mock.assert_called_once_with(URL_TEMPLATE)

    def test_get(self):
        mock = self.mock_http_get(content=WORKBOOKS[0])

        wb = self.workbooks.get(WORKBOOKS[0]['name'])

        self.assertIsNotNone(wb)
        self.assertEqual(w.Workbook(self.workbooks, WORKBOOKS[0]).__dict__,
                         wb.__dict__)
        mock.assert_called_once_with(URL_TEMPLATE_NAME % WORKBOOKS[0]['name'])

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.workbooks.delete(WORKBOOKS[0]['name'])

        mock.assert_called_once_with(URL_TEMPLATE_NAME % WORKBOOKS[0]['name'])

    def test_upload_definition(self):
        mock = self.mock_http_put(None, status_code=200)

        self.workbooks.upload_definition("my_workbook", WB_DEF)

        mock.assert_called_once_with(
            URL_TEMPLATE_DEFINITION % WORKBOOKS[0]['name'],
            WB_DEF,
            headers={'content-type': 'text/plain'})

    def test_get_definition(self):
        mock = self.mock_http_get(status_code=200, content=WB_DEF)

        text = self.workbooks.get_definition("my_workbook")

        self.assertEqual(WB_DEF, text)
        mock.assert_called_once_with(URL_TEMPLATE_DEFINITION
                                     % WORKBOOKS[0]['name'])
