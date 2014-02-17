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

    def _validate_context_str(self, context):
        msg = 'Context must be a dictionary or json compatible string.'

        if not isinstance(context, str):
            raise ex.IllegalArgumentException(msg)

        try:
            json.loads(context)
        except Exception as e:
            raise ex.IllegalArgumentException(msg + e)

    def create(self, workbook_name, task, context=None):
        self._ensure_not_empty(workbook_name=workbook_name, task=task)

        if isinstance(context, dict):
            context_str = str(context)
        else:
            self._validate_context_str(context)
            context_str = context

        data = {
            'workbook_name': workbook_name,
            'task': task,
            'context': context_str
        }

        return self._create('/workbooks/%s/executions' % workbook_name, data)

    def update(self, workbook_name, id, state):
        self._ensure_not_empty(workbook_name=workbook_name, id=id,
                               state=state)

        data = {
            'workbook_name': workbook_name,
            'id': id,
            'state': state
        }

        return self._update('/workbooks/%s/executions/%s' %
                            (workbook_name, id), data)

    def list(self, workbook_name):
        self._ensure_not_empty(workbook_name=workbook_name)

        return self._list('/workbooks/%s/executions' % workbook_name,
                          'executions')

    def get(self, workbook_name, id):
        self._ensure_not_empty(workbook_name=workbook_name, id=id)

        return self._get('/workbooks/%s/executions/%s' % (workbook_name, id))

    def delete(self, workbook_name, id):
        self._ensure_not_empty(workbook_name=workbook_name, id=id)

        self._delete('/workbooks/%s/executions/%s' % (workbook_name, id))
