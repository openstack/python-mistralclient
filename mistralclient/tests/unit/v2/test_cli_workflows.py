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
import six

from mistralclient.api.v2 import workflows
from mistralclient.commands.v2 import base as cmd_base
from mistralclient.commands.v2 import workflows as workflow_cmd
from mistralclient.tests.unit import base


WORKFLOW_DICT = {
    'id': '1-2-3-4',
    'name': 'a',
    'project_id': '12345',
    'tags': ['a', 'b'],
    'input': 'param',
    'created_at': '1',
    'updated_at': '1'
}

WF_DEF = """
version: '2.0'

flow:
  tasks:
    task1:
      action: nova.servers_get server="1"
"""

WF_WITH_DEF_DICT = WORKFLOW_DICT.copy()
WF_WITH_DEF_DICT.update({'definition': WF_DEF})
WORKFLOW = workflows.Workflow(mock, WORKFLOW_DICT)
WORKFLOW_WITH_DEF = workflows.Workflow(mock, WF_WITH_DEF_DICT)


class TestCLIWorkflowsV2(base.BaseCommandTest):
    @mock.patch('argparse.open', create=True)
    def test_create(self, mock_open):
        self.client.workflows.create.return_value = (WORKFLOW,)

        result = self.call(workflow_cmd.Create, app_args=['1.txt'])

        self.assertEqual(
            [('1-2-3-4', 'a', '12345', 'a, b', 'param', '1', '1')],
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    def test_create_public(self, mock_open):
        self.client.workflows.create.return_value = (WORKFLOW,)

        result = self.call(
            workflow_cmd.Create,
            app_args=['1.txt', '--public']
        )

        self.assertEqual(
            [('1-2-3-4', 'a', '12345', 'a, b', 'param', '1', '1')],
            result[1]
        )

        self.assertEqual(
            'public',
            self.client.workflows.create.call_args[1]['scope']
        )

    @mock.patch('argparse.open', create=True)
    def test_create_long_input(self, mock_open):
        wf_long_input_dict = WORKFLOW_DICT.copy()
        long_input = ', '.join(
            ['var%s' % i for i in six.moves.xrange(10)]
        )
        wf_long_input_dict['input'] = long_input
        workflow_long_input = workflows.Workflow(mock, wf_long_input_dict)
        self.client.workflows.create.return_value = (workflow_long_input,)

        result = self.call(workflow_cmd.Create, app_args=['1.txt'])

        self.assertEqual(
            [('1-2-3-4', 'a', '12345', 'a, b', cmd_base.cut(long_input),
              '1', '1')],
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    def test_update(self, mock_open):
        self.client.workflows.update.return_value = (WORKFLOW,)

        result = self.call(workflow_cmd.Update, app_args=['1.txt'])

        self.assertEqual(
            [('1-2-3-4', 'a', '12345', 'a, b', 'param', '1', '1')],
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    def test_update_public(self, mock_open):
        self.client.workflows.update.return_value = (WORKFLOW,)

        result = self.call(
            workflow_cmd.Update,
            app_args=['1.txt', '--public']
        )

        self.assertEqual(
            [('1-2-3-4', 'a', '12345', 'a, b', 'param', '1', '1')],
            result[1]
        )

        self.assertEqual(
            'public',
            self.client.workflows.update.call_args[1]['scope']
        )

    def test_list(self):
        self.client.workflows.list.return_value = (WORKFLOW,)

        result = self.call(workflow_cmd.List)

        self.assertEqual(
            [('1-2-3-4', 'a', '12345', 'a, b', 'param', '1', '1')],
            result[1]
        )

    def test_get(self):
        self.client.workflows.get.return_value = WORKFLOW

        result = self.call(workflow_cmd.Get, app_args=['name'])

        self.assertEqual(
            ('1-2-3-4', 'a', '12345', 'a, b', 'param', '1', '1'),
            result[1]
        )

    def test_delete(self):
        self.call(workflow_cmd.Delete, app_args=['name'])

        self.client.workflows.delete.assert_called_once_with('name')

    def test_delete_with_multi_names(self):
        self.call(workflow_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, self.client.workflows.delete.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            self.client.workflows.delete.call_args_list
        )

    def test_get_definition(self):
        self.client.workflows.get.return_value = WORKFLOW_WITH_DEF

        self.call(workflow_cmd.GetDefinition, app_args=['name'])

        self.app.stdout.write.assert_called_with(WF_DEF)

    @mock.patch('argparse.open', create=True)
    def test_validate(self, mock_open):
        self.client.workflows.validate.return_value = {'valid': True}

        result = self.call(workflow_cmd.Validate, app_args=['wf.yaml'])

        self.assertEqual((True, None), result[1])

    @mock.patch('argparse.open', create=True)
    def test_validate_failed(self, mock_open):
        self.client.workflows.validate.return_value = {
            'valid': False,
            'error': 'Invalid DSL...'
        }

        result = self.call(workflow_cmd.Validate, app_args=['wf.yaml'])

        self.assertEqual((False, 'Invalid DSL...'), result[1])
