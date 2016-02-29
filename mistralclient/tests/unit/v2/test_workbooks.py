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

import pkg_resources as pkg
from six.moves.urllib import parse
from six.moves.urllib import request

from mistralclient.api import base as api_base
from mistralclient.api.v2 import workbooks
from mistralclient.tests.unit.v2 import base

# TODO(everyone): later we need additional tests verifying all the errors etc.


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

INVALID_WB_DEF = """
version: 2.0

name: wb

workflows:
  wf1:
    type: direct
    tasks:
      task1:
        action: std.http url="localhost:8989"
        workflow: wf2
"""

WORKBOOK = {'definition': WB_DEF}

URL_TEMPLATE = '/workbooks'
URL_TEMPLATE_NAME = '/workbooks/%s'
URL_TEMPLATE_VALIDATE = '/workbooks/validate'


class TestWorkbooksV2(base.BaseClientV2Test):
    def test_create(self):
        mock = self.mock_http_post(content=WORKBOOK)

        wb = self.workbooks.create(WB_DEF)

        self.assertIsNotNone(wb)
        self.assertEqual(WB_DEF, wb.definition)

        mock.assert_called_once_with(
            URL_TEMPLATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_create_with_file_uri(self):
        mock = self.mock_http_post(content=WORKBOOK)

        # The contents of wb_v2.yaml must be identical to WB_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/wb_v2.yaml'
        )

        # Convert the file path to file URI
        uri = parse.urljoin('file:', request.pathname2url(path))

        wb = self.workbooks.create(uri)

        self.assertIsNotNone(wb)
        self.assertEqual(WB_DEF, wb.definition)

        mock.assert_called_once_with(
            URL_TEMPLATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_update(self):
        mock = self.mock_http_put(content=WORKBOOK)

        wb = self.workbooks.update(WB_DEF)

        self.assertIsNotNone(wb)
        self.assertEqual(WB_DEF, wb.definition)

        mock.assert_called_once_with(
            URL_TEMPLATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_update_with_file(self):
        mock = self.mock_http_put(content=WORKBOOK)

        # The contents of wb_v2.yaml must be identical to WB_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/wb_v2.yaml'
        )

        wb = self.workbooks.update(path)

        self.assertIsNotNone(wb)
        self.assertEqual(WB_DEF, wb.definition)

        mock.assert_called_once_with(
            URL_TEMPLATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_list(self):
        mock = self.mock_http_get(content={'workbooks': [WORKBOOK]})

        workbook_list = self.workbooks.list()

        self.assertEqual(1, len(workbook_list))

        wb = workbook_list[0]

        self.assertEqual(
            workbooks.Workbook(self.workbooks, WORKBOOK).to_dict(),
            wb.to_dict()
        )

        mock.assert_called_once_with(URL_TEMPLATE)

    def test_get(self):
        mock = self.mock_http_get(content=WORKBOOK)

        wb = self.workbooks.get('wb')

        self.assertIsNotNone(wb)
        self.assertEqual(
            workbooks.Workbook(self.workbooks, WORKBOOK).to_dict(),
            wb.to_dict()
        )

        mock.assert_called_once_with(URL_TEMPLATE_NAME % 'wb')

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.workbooks.delete('wb')

        mock.assert_called_once_with(URL_TEMPLATE_NAME % 'wb')

    def test_validate(self):
        mock = self.mock_http_post(status_code=200,
                                   content={'valid': True})

        result = self.workbooks.validate(WB_DEF)

        self.assertIsNotNone(result)
        self.assertIn('valid', result)
        self.assertTrue(result['valid'])

        mock.assert_called_once_with(
            URL_TEMPLATE_VALIDATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_validate_with_file(self):
        mock = self.mock_http_post(status_code=200,
                                   content={'valid': True})

        # The contents of wb_v2.yaml must be identical to WB_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/wb_v2.yaml'
        )

        result = self.workbooks.validate(path)

        self.assertIsNotNone(result)
        self.assertIn('valid', result)
        self.assertTrue(result['valid'])

        mock.assert_called_once_with(
            URL_TEMPLATE_VALIDATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_validate_failed(self):
        mock_result = {
            "valid": False,
            "error": "Task properties 'action' and 'workflow' "
                     "can't be specified both"
        }

        mock = self.mock_http_post(status_code=200, content=mock_result)

        result = self.workbooks.validate(INVALID_WB_DEF)

        self.assertIsNotNone(result)
        self.assertIn('valid', result)
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        self.assertIn("Task properties 'action' and 'workflow' "
                      "can't be specified both", result['error'])

        mock.assert_called_once_with(
            URL_TEMPLATE_VALIDATE,
            INVALID_WB_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_validate_api_failed(self):
        mock = self.mock_http_post(status_code=500, content={})

        self.assertRaises(api_base.APIException,
                          self.workbooks.validate,
                          WB_DEF)

        mock.assert_called_once_with(
            URL_TEMPLATE_VALIDATE,
            WB_DEF,
            headers={'content-type': 'text/plain'}
        )
