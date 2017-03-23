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

import mock

from mistralclient.api.v2 import cron_triggers
from mistralclient.commands.v2 import cron_triggers as cron_triggers_cmd
from mistralclient.tests.unit import base


TRIGGER_DICT = {
    'name': 'my_trigger',
    'workflow_name': 'flow1',
    'workflow_input': {},
    'workflow_params': {},
    'pattern': '* * * * *',
    'next_execution_time': '4242-12-20 13:37',
    'remaining_executions': 5,
    'created_at': '1',
    'updated_at': '1'
}

TRIGGER = cron_triggers.CronTrigger(mock, TRIGGER_DICT)


class TestCLITriggersV2(base.BaseCommandTest):
    @mock.patch('mistralclient.commands.v2.cron_triggers.Create.'
                '_convert_time_string_to_utc')
    @mock.patch('argparse.open', create=True)
    def test_create(self, mock_open, mock_convert):
        self.client.cron_triggers.create.return_value = TRIGGER
        mock_open.return_value = mock.MagicMock(spec=open)

        result = self.call(
            cron_triggers_cmd.Create,
            app_args=['my_trigger', 'flow1', '--pattern', '* * * * *',
                      '--params', '{}', '--count', '5', '--first-time',
                      '4242-12-20 13:37', '--utc']
        )

        mock_convert.assert_not_called()
        self.assertEqual(
            (
                'my_trigger', 'flow1', {}, '* * * * *',
                '4242-12-20 13:37', 5, '1', '1'
            ),
            result[1]
        )

    @mock.patch('mistralclient.commands.v2.cron_triggers.Create.'
                '_convert_time_string_to_utc')
    @mock.patch('argparse.open', create=True)
    def test_create_no_utc(self, mock_open, mock_convert):
        self.client.cron_triggers.create.return_value = TRIGGER
        mock_open.return_value = mock.MagicMock(spec=open)
        mock_convert.return_value = '4242-12-20 18:37'

        result = self.call(
            cron_triggers_cmd.Create,
            app_args=['my_trigger', 'flow1', '--pattern', '* * * * *',
                      '--params', '{}', '--count', '5', '--first-time',
                      '4242-12-20 13:37']
        )

        mock_convert.assert_called_once_with('4242-12-20 13:37')
        self.client.cron_triggers.create.assert_called_once_with(
            'my_trigger', 'flow1', {}, {}, '* * * * *', '4242-12-20 18:37', 5)
        self.assertEqual(
            (
                'my_trigger', 'flow1', {}, '* * * * *',
                '4242-12-20 13:37', 5, '1', '1'
            ),
            result[1]
        )

    @mock.patch('mistralclient.commands.v2.cron_triggers.time')
    def test_convert_time_string_to_utc_from_utc(self, mock_time):
        cmd = cron_triggers_cmd.Create(self.app, None)

        mock_time.daylight = 0
        mock_time.altzone = 0
        mock_time.timezone = 0
        mock_localtime = mock.Mock()
        mock_localtime.tm_isdst = 0
        mock_time.localtime.return_value = mock_localtime

        utc_value = cmd._convert_time_string_to_utc('4242-12-20 13:37')

        expected_time = '4242-12-20 13:37'

        self.assertEqual(expected_time, utc_value)

    @mock.patch('mistralclient.commands.v2.cron_triggers.time')
    def test_convert_time_string_to_utc_from_dst(self, mock_time):
        cmd = cron_triggers_cmd.Create(self.app, None)

        mock_time.daylight = 1
        mock_time.altzone = (4 * 60 * 60)
        mock_time.timezone = (5 * 60 * 60)
        mock_localtime = mock.Mock()
        mock_localtime.tm_isdst = 1
        mock_time.localtime.return_value = mock_localtime

        utc_value = cmd._convert_time_string_to_utc('4242-12-20 13:37')

        expected_time = '4242-12-20 17:37'

        self.assertEqual(expected_time, utc_value)

    @mock.patch('mistralclient.commands.v2.cron_triggers.time')
    def test_convert_time_string_to_utc_no_dst(self, mock_time):
        cmd = cron_triggers_cmd.Create(self.app, None)

        mock_time.daylight = 1
        mock_time.altzone = (4 * 60 * 60)
        mock_time.timezone = (5 * 60 * 60)
        mock_localtime = mock.Mock()
        mock_localtime.tm_isdst = 0
        mock_time.localtime.return_value = mock_localtime

        utc_value = cmd._convert_time_string_to_utc('4242-12-20 13:37')

        expected_time = '4242-12-20 18:37'

        self.assertEqual(expected_time, utc_value)

    def test_list(self):
        self.client.cron_triggers.list.return_value = [TRIGGER]

        result = self.call(cron_triggers_cmd.List)

        self.assertEqual(
            [(
                'my_trigger', 'flow1', {}, '* * * * *',
                '4242-12-20 13:37', 5, '1', '1'
            )],
            result[1]
        )

    def test_get(self):
        self.client.cron_triggers.get.return_value = TRIGGER

        result = self.call(cron_triggers_cmd.Get, app_args=['name'])

        self.assertEqual(
            (
                'my_trigger', 'flow1', {}, '* * * * *',
                '4242-12-20 13:37', 5, '1', '1'
            ),
            result[1]
        )

    def test_delete(self):
        self.call(cron_triggers_cmd.Delete, app_args=['name'])

        self.client.cron_triggers.delete.assert_called_once_with('name')

    def test_delete_with_multi_names(self):
        self.call(cron_triggers_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, self.client.cron_triggers.delete.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            self.client.cron_triggers.delete.call_args_list
        )
