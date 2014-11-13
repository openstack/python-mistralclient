# Copyright 2014 - Mirantis, Inc.
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

import json

from mistralclient.api import base


class Action(base.Resource):
    resource_name = 'Action'


class ActionManager(base.ResourceManager):
    resource_class = Action

    def create(self, definition):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.post(
            '/actions',
            json.dumps({'definition': definition})
        )

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'actions')]

    def update(self, definition):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.put(
            '/actions',
            json.dumps({'definition': definition})
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'actions')]

    def list(self):
        return self._list('/actions', response_key='actions')

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/actions/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/actions/%s' % name)
