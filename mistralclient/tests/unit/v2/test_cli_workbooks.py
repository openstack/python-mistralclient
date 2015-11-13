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

import mock

from mistralclient.api.v2 import workbooks
from mistralclient.commands.v2 import workbooks as workbook_cmd
from mistralclient.tests.unit import base


WORKBOOK_DICT = {
    'name': 'a',
    'tags': ['a', 'b'],
    'created_at': '1',
    'updated_at': '1'
}


WB_DEF = """
---
version: '2.0

name: wb

workflows:
  wf1:
    tasks:
      task1:
        action: nova.servers_get server="1"
"""

WB_WITH_DEF_DICT = WORKBOOK_DICT.copy()
WB_WITH_DEF_DICT.update({'definition': WB_DEF})
WORKBOOK = workbooks.Workbook(mock, WORKBOOK_DICT)
WORKBOOK_WITH_DEF = workbooks.Workbook(mock, WB_WITH_DEF_DICT)


class TestCLIWorkbooksV2(base.BaseCommandTest):
    @mock.patch('argparse.open', create=True)
    def test_create(self, mock_open):
        self.client.workbooks.create.return_value = WORKBOOK

        result = self.call(workbook_cmd.Create, app_args=['wb.yaml'])

        self.assertEqual(('a', 'a, b', '1', '1'), result[1])

    @mock.patch('argparse.open', create=True)
    def test_update(self, mock_open):
        self.client.workbooks.update.return_value = WORKBOOK

        result = self.call(workbook_cmd.Update, app_args=['definition'])

        self.assertEqual(('a', 'a, b', '1', '1'), result[1])

    def test_list(self):
        self.client.workbooks.list.return_value = (WORKBOOK,)

        result = self.call(workbook_cmd.List)

        self.assertEqual([('a', 'a, b', '1', '1')], result[1])

    def test_get(self):
        self.client.workbooks.get.return_value = WORKBOOK

        result = self.call(workbook_cmd.Get, app_args=['name'])

        self.assertEqual(('a', 'a, b', '1', '1'), result[1])

    def test_delete(self):
        self.call(workbook_cmd.Delete, app_args=['name'])

        self.client.workbooks.delete.assert_called_once_with('name')

    def test_delete_with_multi_names(self):
        self.call(workbook_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, self.client.workbooks.delete.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            self.client.workbooks.delete.call_args_list
        )

    def test_get_definition(self):
        self.client.workbooks.get.return_value = WORKBOOK_WITH_DEF

        self.call(workbook_cmd.GetDefinition, app_args=['name'])

        self.app.stdout.write.assert_called_with(WB_DEF)

    @mock.patch('argparse.open', create=True)
    def test_validate(self, mock_open):
        self.client.workbooks.validate.return_value = {'valid': True}

        result = self.call(workbook_cmd.Validate, app_args=['wb.yaml'])

        self.assertEqual((True, None), result[1])

    @mock.patch('argparse.open', create=True)
    def test_validate_failed(self, mock_open):
        self.client.workbooks.validate.return_value = {
            'valid': False,
            'error': 'Invalid DSL...'
        }

        result = self.call(workbook_cmd.Validate, app_args=['wb.yaml'])

        self.assertEqual((False, 'Invalid DSL...'), result[1])
