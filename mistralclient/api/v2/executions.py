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

from oslo_utils import uuidutils

from mistralclient.api import base


class Execution(base.Resource):
    resource_name = 'Execution'


class ExecutionManager(base.ResourceManager):
    resource_class = Execution

    def create(self, workflow_identifier='', namespace='',
               workflow_input=None, description='', source_execution_id=None,
               **params):
        ident = workflow_identifier or source_execution_id
        self._ensure_not_empty(workflow_identifier=ident)

        data = {
            'description': description,
        }

        if uuidutils.is_uuid_like(source_execution_id):
            data.update({'source_execution_id': source_execution_id})

        if workflow_identifier:
            if uuidutils.is_uuid_like(workflow_identifier):
                data.update({'workflow_id': workflow_identifier})
            else:
                data.update({'workflow_name': workflow_identifier})

        if namespace:
            data.update({'workflow_namespace': namespace})

        if workflow_input:
            if isinstance(workflow_input, six.string_types):
                data.update({'input': workflow_input})
            else:
                data.update({'input': json.dumps(workflow_input)})

        if params:
            data.update({'params': json.dumps(params)})

        return self._create('/executions', data)

    def update(self, id, state, description=None, env=None):
        data = {}

        if state:
            data['state'] = state

        if description:
            data['description'] = description

        if env:
            data['params'] = {'env': env}

        return self._update('/executions/%s' % id, data)

    def list(self, task=None, marker='', limit=None, sort_keys='',
             sort_dirs='', fields='', **filters):
        if task:
            filters['task_execution_id'] = task

        query_string = self._build_query_params(
            marker=marker,
            limit=limit,
            sort_keys=sort_keys,
            sort_dirs=sort_dirs,
            fields=fields,
            filters=filters
        )

        return self._list(
            '/executions%s' % query_string,
            response_key='executions',
        )

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/executions/%s' % id)

    def delete(self, id, force=None):
        self._ensure_not_empty(id=id)
        qparams = {}
        if force:
            qparams['force'] = True

        query_string = self._build_query_params(filters=qparams)

        self._delete('/executions/%s%s' % (id, query_string))
