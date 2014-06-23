# -*- coding: utf-8 -*-
#
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

import json

from mistralclient.api import base
from mistralclient import exceptions as ex


class Execution(base.Resource):
    resource_name = 'Execution'


class ExecutionManager(base.ResourceManager):
    resource_class = Execution

    def _get_context_as_str(self, context):
        msg = 'Context must be a dictionary or json compatible string:'

        try:
            if isinstance(context, dict):
                context = json.dumps(context)
            else:
                json.loads(context)
        except Exception as e:
            raise ex.IllegalArgumentException(' '.join((msg, str(e))))

        return context

    def create(self, workbook_name, task, context=None):
        self._ensure_not_empty(workbook_name=workbook_name, task=task)

        data = {
            'workbook_name': workbook_name,
            'task': task
        }

        if context:
            data['context'] = self._get_context_as_str(context)

        return self._create('/workbooks/%s/executions' % workbook_name, data)

    def update(self, workbook_name, id, state):
        self._ensure_not_empty(id=id, state=state)

        data = {
            'state': state
        }

        if workbook_name:
            uri = '/workbooks/%s/executions/%s' % (workbook_name, id)
        else:
            uri = '/executions/%s' % id

        return self._update(uri, data)

    def list(self, workbook_name):
        if workbook_name:
            uri = '/workbooks/%s/executions' % workbook_name
        else:
            uri = '/executions'

        return self._list(uri, 'executions')

    def get(self, workbook_name, id):
        self._ensure_not_empty(id=id)

        if workbook_name:
            uri = '/workbooks/%s/executions/%s' % (workbook_name, id)
        else:
            uri = '/executions/%s' % id

        return self._get(uri)

    def delete(self, workbook_name, id):
        self._ensure_not_empty(id=id)

        if workbook_name:
            uri = '/workbooks/%s/executions/%s' % (workbook_name, id)
        else:
            uri = '/executions/%s' % id

        self._delete(uri)
