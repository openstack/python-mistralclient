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

from oslo_serialization import jsonutils

from mistralclient.api import base
from mistralclient.api.v2 import executions


class Task(base.Resource):
    resource_name = 'Task'


class TaskManager(base.ResourceManager):
    resource_class = Task

    def list(self, workflow_execution_id=None, marker='', limit=None,
             sort_keys='', sort_dirs='', fields=None, **filters):
        url = '/tasks'

        if workflow_execution_id:
            url = '/executions/%s/tasks' % workflow_execution_id

        url += '%s'

        query_string = self._build_query_params(
            marker=marker,
            limit=limit,
            sort_keys=sort_keys,
            sort_dirs=sort_dirs,
            fields=fields,
            filters=filters
        )

        return self._list(url % query_string, response_key='tasks')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/tasks/%s' % id)

    def get_task_sub_executions(self, id, errors_only='', max_depth=-1):
        task_sub_execs_path = '/tasks/%s/executions%s'
        params = '?max_depth=%s&errors_only=%s' % (max_depth, errors_only)

        return self._list(
            task_sub_execs_path % (id, params),
            response_key='executions',
            returned_res_cls=executions.Execution
        )

    def rerun(self, task_ex_id, reset=True, env=None):
        url = '/tasks/%s' % task_ex_id

        body = {
            'id': task_ex_id,
            'state': 'RUNNING',
            'reset': reset
        }

        if env:
            body['env'] = jsonutils.dumps(env)

        return self._update(url, body)
