# Copyright 2013 - Mirantis, Inc.
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

    def update(self, workbook_name, execution_id, id, state):
        self._ensure_not_empty(id=id, state=state)

        data = {
            'state': state
        }

        if execution_id:
            if workbook_name:
                uri = ('/workbooks/%s/executions/%s/tasks/%s' %
                       (workbook_name, execution_id, id))
            else:
                uri = '/executions/%s/tasks/%s' % (execution_id, id)
        else:
            uri = '/tasks/%s' % id

        return self._update(uri, data)

    def list(self, workbook_name, execution_id):
        if execution_id:
            if workbook_name:
                uri = ('/workbooks/%s/executions/%s/tasks' %
                       (workbook_name, execution_id))
            else:
                uri = '/executions/%s/tasks' % execution_id
        else:
            uri = '/tasks'

        return self._list(uri, 'tasks')

    def get(self, workbook_name, execution_id, id):
        self._ensure_not_empty(id=id)

        if execution_id:
            if workbook_name:
                uri = ('/workbooks/%s/executions/%s/tasks/%s' %
                       (workbook_name, execution_id, id))
            else:
                uri = '/executions/%s/tasks/%s' % (execution_id, id)
        else:
            uri = '/tasks/%s' % id

        return self._get(uri)
