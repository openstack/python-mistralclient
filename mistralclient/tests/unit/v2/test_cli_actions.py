# Copyright 2014 Mirantis, Inc.
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
import six

from mistralclient.api.v2 import actions
from mistralclient.commands.v2 import actions as action_cmd
from mistralclient.commands.v2 import base as cmd_base
from mistralclient.tests.unit import base


ACTION_DICT = {
    'name': 'a',
    'is_system': True,
    'input': "param1",
    'description': 'My cool action',
    'tags': ['test'],
    'created_at': '1',
    'updated_at': '1'
}

ACTION_DEF = """
---
version: '2.0'

base: std.echo
base-parameters:
    output: "<% $.str1 %><% $.str2 %>"
output: "<% $ %><% $ %>"
"""

ACTION_WITH_DEF_DICT = ACTION_DICT.copy()
ACTION_WITH_DEF_DICT.update({'definition': ACTION_DEF})
ACTION = actions.Action(mock, ACTION_DICT)
ACTION_WITH_DEF = actions.Action(mock, ACTION_WITH_DEF_DICT)


class TestCLIActionsV2(base.BaseCommandTest):
    @mock.patch('argparse.open', create=True)
    @mock.patch('mistralclient.api.v2.actions.ActionManager.create')
    def test_create(self, mock, mock_open):
        mock.return_value = (ACTION,)

        result = self.call(action_cmd.Create, app_args=['1.txt'])

        self.assertEqual(
            [('a', True, "param1", 'My cool action', 'test', '1', '1')],
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    @mock.patch('mistralclient.api.v2.actions.ActionManager.create')
    def test_create_public(self, mock, mock_open):
        mock.return_value = (ACTION,)

        result = self.call(
            action_cmd.Create,
            app_args=['1.txt', '--public']
        )

        self.assertEqual(
            [('a', True, "param1", 'My cool action', 'test', '1', '1')],
            result[1]
        )

        self.assertEqual('public', mock.call_args[1]['scope'])

    @mock.patch('argparse.open', create=True)
    @mock.patch('mistralclient.api.v2.actions.ActionManager.create')
    def test_create_long_input(self, mock, mock_open):
        action_long_input_dict = ACTION_DICT.copy()
        long_input = ', '.join(
            ['var%s' % i for i in six.moves.xrange(10)]
        )
        action_long_input_dict['input'] = long_input
        workflow_long_input = actions.Action(mock, action_long_input_dict)
        mock.return_value = (workflow_long_input,)

        result = self.call(action_cmd.Create, app_args=['1.txt'])

        self.assertEqual(
            [('a', True, cmd_base.cut(long_input),
              'My cool action', 'test', '1', '1')],
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    @mock.patch('mistralclient.api.v2.actions.ActionManager.update')
    def test_update(self, mock, mock_open):
        mock.return_value = (ACTION,)

        result = self.call(action_cmd.Update, app_args=['my_action.yaml'])

        self.assertEqual(
            [('a', True, "param1", 'My cool action', 'test', '1', '1')],
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    @mock.patch('mistralclient.api.v2.actions.ActionManager.update')
    def test_update_public(self, mock, mock_open):
        mock.return_value = (ACTION,)

        result = self.call(
            action_cmd.Update,
            app_args=['my_action.yaml', '--public']
        )

        self.assertEqual(
            [('a', True, "param1", 'My cool action', 'test', '1', '1')],
            result[1]
        )

        self.assertEqual('public', mock.call_args[1]['scope'])

    @mock.patch('mistralclient.api.v2.actions.ActionManager.list')
    def test_list(self, mock):
        mock.return_value = (ACTION,)

        result = self.call(action_cmd.List)

        self.assertEqual(
            [('a', True, "param1", 'My cool action', 'test', '1', '1')],
            result[1]
        )

    @mock.patch('mistralclient.api.v2.actions.ActionManager.get')
    def test_get(self, mock):
        mock.return_value = ACTION

        result = self.call(action_cmd.Get, app_args=['name'])

        self.assertEqual(
            ('a', True, "param1", 'My cool action', 'test', '1', '1'),
            result[1]
        )

    @mock.patch('mistralclient.api.v2.actions.ActionManager.delete')
    def test_delete(self, del_mock):
        self.call(action_cmd.Delete, app_args=['name'])

        del_mock.assert_called_once_with('name')

    @mock.patch('mistralclient.api.v2.actions.ActionManager.delete')
    def test_delete_with_multi_names(self, del_mock):
        self.call(action_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, del_mock.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            del_mock.call_args_list
        )

    @mock.patch('mistralclient.api.v2.actions.'
                'ActionManager.get')
    def test_get_definition(self, mock):
        mock.return_value = ACTION_WITH_DEF

        self.call(action_cmd.GetDefinition, app_args=['name'])

        self.app.stdout.write.assert_called_with(ACTION_DEF)
