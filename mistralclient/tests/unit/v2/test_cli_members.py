# Copyright 2016 Catalyst IT Limited
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

from unittest import mock

from mistralclient.api.v2 import members
from mistralclient.commands.v2 import members as member_cmd
from mistralclient.tests.unit import base

MEMBER_DICT = {
    'id': '123',
    'resource_id': '456',
    'resource_type': 'workflow',
    'project_id': '1111',
    'member_id': '2222',
    'status': 'pending',
    'created_at': '1',
    'updated_at': '1'
}

MEMBER = members.Member(mock, MEMBER_DICT)


class TestCLIWorkflowMembers(base.BaseCommandTest):
    def test_create(self):
        self.client.members.create.return_value = MEMBER

        result = self.call(
            member_cmd.Create,
            app_args=[MEMBER_DICT['resource_id'], MEMBER_DICT['resource_type'],
                      MEMBER_DICT['member_id']]
        )

        self.assertEqual(
            ('456', 'workflow', '1111', '2222', 'pending', '1', '1'),
            result[1]
        )

    def test_update(self):
        self.client.members.update.return_value = MEMBER

        result = self.call(
            member_cmd.Update,
            app_args=[MEMBER_DICT['resource_id'], MEMBER_DICT['resource_type'],
                      '-m', MEMBER_DICT['member_id']]
        )

        self.assertEqual(
            ('456', 'workflow', '1111', '2222', 'pending', '1', '1'),
            result[1]
        )

    def test_list(self):
        self.client.members.list.return_value = [MEMBER]

        result = self.call(
            member_cmd.List,
            app_args=[MEMBER_DICT['resource_id'], MEMBER_DICT['resource_type']]
        )

        self.assertListEqual(
            [('456', 'workflow', '1111', '2222', 'pending', '1', '1')],
            result[1]
        )

    def test_get(self):
        self.client.members.get.return_value = MEMBER

        result = self.call(
            member_cmd.Get,
            app_args=[MEMBER_DICT['resource_id'], MEMBER_DICT['resource_type'],
                      '-m', MEMBER_DICT['member_id']]
        )

        self.assertEqual(
            ('456', 'workflow', '1111', '2222', 'pending', '1', '1'),
            result[1]
        )

    def test_delete(self):
        self.call(
            member_cmd.Delete,
            app_args=[MEMBER_DICT['resource_id'], MEMBER_DICT['resource_type'],
                      MEMBER_DICT['member_id']]
        )

        self.client.members.delete.assert_called_once_with(
            MEMBER_DICT['resource_id'],
            MEMBER_DICT['resource_type'],
            MEMBER_DICT['member_id']
        )
