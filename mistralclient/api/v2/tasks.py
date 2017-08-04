# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
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


class Task(base.Resource):
    resource_name = 'Task'


class TaskManager(base.ResourceManager):
    resource_class = Task

    def list(self, workflow_execution_id=None, marker='', limit=None,
             sort_keys='', sort_dirs='', fields=[], **filters):
        url = '/tasks'

        if workflow_execution_id:
            url = '/executions/%s/tasks' % workflow_execution_id

        url += '%s'

        qparams = {}

        if marker:
            qparams['marker'] = marker

        if limit:
            qparams['limit'] = limit

        if sort_keys:
            qparams['sort_keys'] = sort_keys

        if sort_dirs:
            qparams['sort_dirs'] = sort_dirs

        if fields:
            qparams['fields'] = ",".join(fields)

        for name, val in filters.items():
            qparams[name] = val

        query_string = ("?%s" % urlparse.urlencode(list(qparams.items()))
                        if qparams else "")

        return self._list(url % query_string, response_key='tasks')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/tasks/%s' % id)

    def rerun(self, task_ex_id, reset=True, env=None):
        url = '/tasks/%s' % task_ex_id

        body = {
            'id': task_ex_id,
            'state': 'RUNNING',
            'reset': reset
        }

        if env:
            body['env'] = json.dumps(env)

        return self._update(url, body)
