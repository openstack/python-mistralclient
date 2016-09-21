# Copyright 2016 - Catalyst IT Limited
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

from mistralclient.api import base


class Member(base.Resource):
    resource_name = 'Member'


class MemberManager(base.ResourceManager):
    resource_class = Member

    def create(self, resource_id, resource_type, member_id):
        self._ensure_not_empty(
            resource_id=resource_id,
            resource_type=resource_type,
            member_id=member_id
        )

        data = {
            'member_id': member_id,
        }

        url = '/%ss/%s/members' % (resource_type, resource_id)

        return self._create(url, data)

    def update(self, resource_id, resource_type, member_id='',
               status='accepted'):
        if not member_id:
            member_id = self.http_client.project_id

        url = '/%ss/%s/members/%s' % (resource_type, resource_id, member_id)

        return self._update(url, {'status': status})

    def list(self, resource_id, resource_type):
        url = '/%ss/%s/members' % (resource_type, resource_id)

        return self._list(url, response_key='members')

    def get(self, resource_id, resource_type, member_id=None):
        self._ensure_not_empty(
            resource_id=resource_id,
            resource_type=resource_type,
        )

        if not member_id:
            member_id = self.http_client.project_id

        url = '/%ss/%s/members/%s' % (resource_type, resource_id, member_id)

        return self._get(url)

    def delete(self, resource_id, resource_type, member_id):
        self._ensure_not_empty(
            resource_id=resource_id,
            resource_type=resource_type,
            member_id=member_id
        )

        url = '/%ss/%s/members/%s' % (resource_type, resource_id, member_id)

        self._delete(url)
