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


class Execution(base.Resource):
    resource_name = 'Execution'


class ExecutionManager(base.ResourceManager):
    resource_class = Execution

    def create(self, workflow_name, workflow_input=None, **params):
        self._ensure_not_empty(workflow_name=workflow_name)

        data = {'workflow_name': workflow_name}

        if workflow_input:
            data.update({'input': json.dumps(workflow_input)})

        if params:
            data.update({'params': json.dumps(params)})

        return self._create('/executions', data)

    def create_reverse_workflow(self, workflow_name, workflow_input,
                                task_name, **params):
        params.update({'task_name': task_name})

        return self.create(workflow_name, workflow_input, **params)

    def create_direct_workflow(self, workflow_name, workflow_input, **params):
        return self.create(workflow_name, workflow_input, **params)

    def update(self, id, state):
        self._ensure_not_empty(id=id, state=state)

        data = {
            'state': state
        }

        return self._update('/executions/%s' % id, data)

    def list(self):
        return self._list('/executions', response_key='executions')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/executions/%s' % id)

    def delete(self, id):
        self._ensure_not_empty(id=id)

        self._delete('/executions/%s' % id)
