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

from mistralclient.api import base


class Task(base.Resource):
    resource_name = 'Task'


class TaskManager(base.ResourceManager):
    resource_class = Task

    def update(self, id, state):
        self._ensure_not_empty(id=id, state=state)

        data = {
            'state': state
        }

        return self._update('/tasks/%s' % id, data)

    def list(self):
        return self._list('/tasks', response_key='tasks')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/tasks/%s' % id)
