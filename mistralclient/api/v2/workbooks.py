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
from mistralclient import utils


class Workbook(base.Resource):
    resource_name = 'Workbook'


class WorkbookManager(base.ResourceManager):
    resource_class = Workbook

    def _get_workbooks_url(self, resource=None, namespace=None, scope=None):
        url = '/workbooks'

        if resource:
            url += '/%s' % resource

        if scope and namespace:
            url += '?scope=%s&namespace=%s' % (scope, namespace)
        elif scope:
            url += '?scope=%s' % scope
        elif namespace:
            url += '?namespace=%s' % namespace

        return url

    def create(self, definition, namespace='', scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._create(
            self._get_workbooks_url(None, namespace, scope),
            definition,
            dump_json=False,
            headers={'content-type': 'text/plain'}
        )

    def update(self, definition, namespace='', scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._update(
            self._get_workbooks_url(None, namespace, scope),
            definition,
            dump_json=False,
            headers={'content-type': 'text/plain'}
        )

    def list(self, namespace='', marker='', limit=None, sort_keys='',
             sort_dirs='', fields='', **filters):
        query_string = self._build_query_params(
            marker=marker,
            limit=limit,
            sort_keys=sort_keys,
            sort_dirs=sort_dirs,
            filters=filters,
            namespace=namespace
        )

        return self._list(
            '/workbooks{}'.format(query_string),
            response_key='workbooks'
        )

    def get(self, name, namespace=''):
        self._ensure_not_empty(name=name)

        return self._get(
            self._get_workbooks_url(name, namespace)
        )

    def delete(self, name, namespace=''):
        self._ensure_not_empty(name=name)

        self._delete(self._get_workbooks_url(name, namespace))

    def validate(self, definition):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._validate(
            '/workbooks/validate',
            definition,
            dump_json=False,
            headers={'content-type': 'text/plain'}
        )
