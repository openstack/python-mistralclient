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
import six

from mistralclient.api import base

urlparse = six.moves.urllib.parse


class ActionExecution(base.Resource):
    resource_name = 'ActionExecution'


class ActionExecutionManager(base.ResourceManager):
    resource_class = ActionExecution

    def create(self, name, input=None, **params):
        self._ensure_not_empty(name=name)

        data = {'name': name}

        if input:
            data['input'] = json.dumps(input)

        if params:
            data['params'] = json.dumps(params)

        resp = self.http_client.post(
            '/action_executions',
            json.dumps(data)
        )

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.get_json(resp))

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

    def list(self, task_execution_id=None, limit=None):
        url = '/action_executions'

        if task_execution_id:
            url = '/tasks/%s/action_executions' % task_execution_id

        url += "%s"

        qparams = {}

        if limit:
            qparams['limit'] = limit

        query_string = ("?%s" % urlparse.urlencode(list(qparams.items()))
                        if qparams else "")

        return self._list(url % query_string, response_key='action_executions')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/action_executions/%s' % id)

    def delete(self, id):
        self._ensure_not_empty(id=id)

        self._delete('/action_executions/%s' % id)
