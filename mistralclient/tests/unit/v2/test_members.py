# Copyright 2016 Catalyst IT Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import copy
import json

from mistralclient.tests.unit.v2 import base

MEMBER = {
    'id': '123',
    'resource_id': '456',
    'resource_type': 'workflow',
    'project_id': 'dc4ffdee54d74028b19b1b90e77aa84f',
    'member_id': '04f61e967fa14cd49950ffe2319317ad',
    'status': 'pending',
}

WORKFLOW_MEMBERS_URL = '/workflows/%s/members' % (MEMBER['resource_id'])
WORKFLOW_MEMBER_URL = '/workflows/%s/members/%s' % (
    MEMBER['resource_id'], MEMBER['member_id']
)


class TestWorkflowMembers(base.BaseClientV2Test):
    def test_create(self):
        mock = self.mock_http_post(content=MEMBER)

        mb = self.members.create(
            MEMBER['resource_id'],
            MEMBER['resource_type'],
            MEMBER['member_id']
        )

        self.assertIsNotNone(mb)

        mock.assert_called_once_with(
            WORKFLOW_MEMBERS_URL,
            json.dumps({'member_id': MEMBER['member_id']})
        )

    def test_update(self):
        updated_member = copy.copy(MEMBER)
        updated_member['status'] = 'accepted'

        mock = self.mock_http_put(content=updated_member)

        mb = self.members.update(
            MEMBER['resource_id'],
            MEMBER['resource_type'],
            MEMBER['member_id']
        )

        self.assertIsNotNone(mb)

        mock.assert_called_once_with(
            WORKFLOW_MEMBER_URL,
            json.dumps({"status": "accepted"})
        )

    def test_list(self):
        mock = self.mock_http_get(content={'members': [MEMBER]})

        mbs = self.members.list(MEMBER['resource_id'], MEMBER['resource_type'])

        self.assertEqual(1, len(mbs))

        mock.assert_called_once_with(WORKFLOW_MEMBERS_URL)

    def test_get(self):
        mock = self.mock_http_get(content=MEMBER)

        mb = self.members.get(
            MEMBER['resource_id'],
            MEMBER['resource_type'],
            MEMBER['member_id']
        )

        self.assertIsNotNone(mb)

        mock.assert_called_once_with(WORKFLOW_MEMBER_URL)

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.members.delete(
            MEMBER['resource_id'],
            MEMBER['resource_type'],
            MEMBER['member_id']
        )

        mock.assert_called_once_with(WORKFLOW_MEMBER_URL)
