# Copyright 2014 Mirantis, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from unittest import mock

from mistralclient.api.v2 import event_triggers
from mistralclient.commands.v2 import event_triggers as event_triggers_cmd
from mistralclient.tests.unit import base


TRIGGER_DICT = {
    'id': '456',
    'name': 'my_trigger',
    'workflow_id': '123e4567-e89b-12d3-a456-426655440000',
    'workflow_input': {},
    'workflow_params': {},
    'exchange': 'dummy_exchange',
    'topic': 'dummy_topic',
    'event': 'event.dummy',
    'created_at': '1',
    'updated_at': '1'
}

TRIGGER = event_triggers.EventTrigger(mock, TRIGGER_DICT)


class TestCLITriggersV2(base.BaseCommandTest):

    @mock.patch('argparse.open', create=True)
    def test_create(self, mock_open):
        self.client.event_triggers.create.return_value = TRIGGER
        mock_open.return_value = mock.MagicMock(spec=open)

        result = self.call(
            event_triggers_cmd.Create,
            app_args=['my_trigger', '123e4567-e89b-12d3-a456-426655440000',
                      'dummy_exchange', 'dummy_topic', 'event.dummy',
                      '--params', '{}']
        )

        self.assertEqual(
            (
                '456', 'my_trigger', '123e4567-e89b-12d3-a456-426655440000',
                {}, 'dummy_exchange', 'dummy_topic', 'event.dummy', '1', '1'
            ),
            result[1]
        )

    def test_list(self):
        self.client.event_triggers.list.return_value = [TRIGGER]

        result = self.call(event_triggers_cmd.List)

        self.assertEqual(
            [(
                '456', 'my_trigger', '123e4567-e89b-12d3-a456-426655440000',
                {}, 'dummy_exchange', 'dummy_topic', 'event.dummy', '1', '1'
            )],
            result[1]
        )

    def test_get(self):
        self.client.event_triggers.get.return_value = TRIGGER

        result = self.call(event_triggers_cmd.Get, app_args=['id'])

        self.assertEqual(
            (
                '456', 'my_trigger', '123e4567-e89b-12d3-a456-426655440000',
                {}, 'dummy_exchange', 'dummy_topic', 'event.dummy', '1', '1'
            ),
            result[1]
        )

    def test_delete(self):
        self.call(event_triggers_cmd.Delete, app_args=['id'])

        self.client.event_triggers.delete.assert_called_once_with('id')

    def test_delete_with_multi_names(self):
        self.call(event_triggers_cmd.Delete, app_args=['id1', 'id2'])

        self.assertEqual(2, self.client.event_triggers.delete.call_count)
        self.assertEqual(
            [mock.call('id1'), mock.call('id2')],
            self.client.event_triggers.delete.call_args_list
        )
