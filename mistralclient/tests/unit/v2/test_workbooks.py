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

from mistralclient.tests.unit.v2 import base
from mistralclient.api.v2 import workbooks

# TODO: later we need additional tests verifying all the errors etc.


WB_DEF = """
---
version: 2.0

name: wb

workflows:
  wf1:
    type: direct
    input:
      - param1
      - param2

    tasks:
      task1:
        action: std.http url="localhost:8989"
        on-success:
          - test_subsequent

      test_subsequent:
        action: std.http url="http://some_url" server_id=1
"""

WORKBOOK = {'definition': WB_DEF}


URL_TEMPLATE = '/workbooks'
URL_TEMPLATE_NAME = '/workbooks/%s'


class TestWorkbooksV2(base.BaseClientV2Test):
    def test_create(self):
        mock = self.mock_http_post(content=WORKBOOK)

        wb = self.workbooks.create(WORKBOOK['definition'])

        self.assertIsNotNone(wb)
        self.assertEqual(
            workbooks.Workbook(self.workbooks, WORKBOOK).__dict__,
            wb.__dict__
        )

        mock.assert_called_once_with(URL_TEMPLATE, json.dumps(WORKBOOK))

    def test_update(self):
        mock = self.mock_http_put(content=WORKBOOK)

        wb = self.workbooks.update(WORKBOOK['definition'])

        self.assertIsNotNone(wb)
        self.assertEqual(
            workbooks.Workbook(self.workbooks, WORKBOOK).__dict__,
            wb.__dict__
        )

        mock.assert_called_once_with(URL_TEMPLATE, json.dumps(WORKBOOK))

    def test_list(self):
        mock = self.mock_http_get(content={'workbooks': [WORKBOOK]})

        workbook_list = self.workbooks.list()

        self.assertEqual(1, len(workbook_list))

        wb = workbook_list[0]

        self.assertEqual(
            workbooks.Workbook(self.workbooks, WORKBOOK).__dict__,
            wb.__dict__
        )

        mock.assert_called_once_with(URL_TEMPLATE)

    def test_get(self):
        mock = self.mock_http_get(content=WORKBOOK)

        wb = self.workbooks.get('wb')

        self.assertIsNotNone(wb)
        self.assertEqual(
            workbooks.Workbook(self.workbooks, WORKBOOK).__dict__,
            wb.__dict__
        )

        mock.assert_called_once_with(URL_TEMPLATE_NAME % 'wb')

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.workbooks.delete('wb')

        mock.assert_called_once_with(URL_TEMPLATE_NAME % 'wb')
