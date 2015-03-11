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


class ActionExecution(base.Resource):
    resource_name = 'ActionExecution'


class ActionExecutionManager(base.ResourceManager):
    resource_class = ActionExecution

    def update(self, id, state=None, output=None):
        self._ensure_not_empty(id=id)

        if not (state or output):
            raise base.APIException(
                400,
                "Please provide either state or output for action execution."
            )

        data = {}
        if state:
            data['state'] = state

        if output:
            data['output'] = output

        return self._update('/action_executions/%s' % id, data)

    def list(self, task_execution_id=None):
        url = '/action_executions'

        if task_execution_id:
            url = '/tasks/%s/action_executions' % task_execution_id

        return self._list(url, response_key='action_executions')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/action_executions/%s' % id)
