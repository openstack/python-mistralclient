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

from mistralclient.api import base


class Workflow(base.Resource):
    resource_name = 'Workflow'


class WorkflowManager(base.ResourceManager):
    resource_class = Workflow

    def create(self, definition, namespace='', scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = self.get_contents_if_file(definition)

        return self._create(
            '/workflows?scope=%s&namespace=%s' % (scope, namespace),
            definition,
            response_key='workflows',
            dump_json=False,
            headers={'content-type': 'text/plain'},
            is_iter_resp=True
        )

    def update(self, definition, namespace='', scope='private', id=None):
        self._ensure_not_empty(definition=definition)

        url_pre = ('/workflows/%s' % id) if id else '/workflows'

        # If the specified definition is actually a file, read in the
        # definition file
        definition = self.get_contents_if_file(definition)

        is_iter_resp = True
        response_key = 'workflows'

        if id:
            is_iter_resp = False
            response_key = None

        return self._update(
            '%s?namespace=%s&scope=%s' % (url_pre, namespace, scope),
            definition,
            response_key=response_key,
            dump_json=False,
            headers={'content-type': 'text/plain'},
            is_iter_resp=is_iter_resp,
        )

    def list(self, namespace='', marker='', limit=None, sort_keys='',
             sort_dirs='', fields='', **filters):
        if namespace:
            filters['namespace'] = namespace

        query_string = self._build_query_params(
            marker=marker,
            limit=limit,
            sort_keys=sort_keys,
            sort_dirs=sort_dirs,
            fields=fields,
            filters=filters
        )

        return self._list(
            '/workflows%s' % query_string,
            response_key='workflows',
        )

    def get(self, identifier, namespace=''):
        self._ensure_not_empty(identifier=identifier)

        return self._get(
            '/workflows/%s?namespace=%s' % (identifier, namespace)
        )

    def delete(self, identifier, namespace=None):
        self._ensure_not_empty(identifier=identifier)

        path = '/workflows/%s' % identifier

        if namespace:
            path = path + '?namespace=%s' % namespace

        self._delete(path)

    def validate(self, definition):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = self.get_contents_if_file(definition)

        return self._validate(
            '/workflows/validate',
            definition,
            dump_json=False,
            headers={'content-type': 'text/plain'}
        )
