# Copyright 2014 StackStorm, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import mock

from mistralclient.tests.unit import base

from mistralclient.commands.v1 import workbooks
from mistralclient.api.v1.workbooks import Workbook

WORKBOOK = Workbook(mock, {
    'name': 'a',
    'description': 'some',
    'tags': ['a', 'b']
})


class TestCLIWorkbooks(base.BaseCommandTest):
    @mock.patch('mistralclient.api.v1.workbooks.WorkbookManager.create')
    def test_create(self, mock):
        mock.return_value = WORKBOOK

        result = self.call(workbooks.Create, app_args=['name'])

        self.assertEqual(('a', 'some', 'a, b'), result[1])

    @mock.patch('mistralclient.api.v1.workbooks.WorkbookManager.update')
    def test_update(self, mock):
        mock.return_value = WORKBOOK

        result = self.call(workbooks.Update, app_args=['name'])

        self.assertEqual(('a', 'some', 'a, b'), result[1])

    @mock.patch('mistralclient.api.v1.workbooks.WorkbookManager.list')
    def test_list(self, mock):
        mock.return_value = (WORKBOOK,)

        result = self.call(workbooks.List)

        self.assertEqual([('a', 'some', 'a, b')], result[1])

    @mock.patch('mistralclient.api.v1.workbooks.WorkbookManager.get')
    def test_get(self, mock):
        mock.return_value = WORKBOOK

        result = self.call(workbooks.Get, app_args=['name'])

        self.assertEqual(('a', 'some', 'a, b'), result[1])

    @mock.patch('mistralclient.api.v1.workbooks.WorkbookManager.delete')
    def test_delete(self, mock):
        self.assertIsNone(self.call(workbooks.Delete, app_args=['name']))

    @mock.patch('argparse.open', create=True)
    @mock.patch(
        'mistralclient.api.v1.workbooks.WorkbookManager.upload_definition'
    )
    def test_upload_definition(self, mock, mock_open):
        mock.return_value = WORKBOOK
        mock_open.return_value = mock.MagicMock(spec=file)

        result = self.call(workbooks.UploadDefinition,
                           app_args=['name', '1.txt'])

        self.assertIsNone(result)

    @mock.patch('mistralclient.api.v1.workbooks.'
                'WorkbookManager.get_definition')
    def test_get_definition(self, mock):
        mock.return_value = 'sometext'

        self.call(workbooks.GetDefinition, app_args=['name'])

        self.app.stdout.write.assert_called_with('sometext')
