# Copyright 2020 Nokia Software.
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

from oslo_utils import uuidutils

from mistralclient.api import base


class DynamicAction(base.Resource):
    resource_name = 'DynamicAction'


class DynamicActionManager(base.ResourceManager):
    resource_class = DynamicAction

    def get(self, identifier, namespace=''):
        self._ensure_not_empty(identifier=identifier)

        return self._get(
            '/dynamic_actions/%s?namespace=%s' % (identifier, namespace)
        )

    def create(self, name, class_name, code_source, scope='private',
               namespace=''):
        self._ensure_not_empty(
            name=name,
            class_name=class_name,
            code_source=code_source
        )

        data = {
            "name": name,
            "class_name": class_name,
            "scope": scope,
            "namespace": namespace
        }

        if uuidutils.is_uuid_like(code_source):
            data['code_source_id'] = code_source
        else:
            data['code_source_name'] = code_source

        return self._create('/dynamic_actions', data)

    def update(self, identifier, class_name=None, code_source=None,
               scope='private', namespace=''):
        self._ensure_not_empty(identifier=identifier)

        data = {
            'scope': scope,
            'namespace': namespace
        }

        if uuidutils.is_uuid_like(identifier):
            data['id'] = identifier
        else:
            data['name'] = identifier

        if class_name:
            data['class_name'] = class_name

        if code_source:
            if uuidutils.is_uuid_like(code_source):
                data['code_source_id'] = code_source
            else:
                data['code_source_name'] = code_source

        return self._update('/dynamic_actions', data)

    def list(self, marker='', limit=None, sort_keys='', sort_dirs='',
             fields='', namespace='', **filters):
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
            '/dynamic_actions%s' % query_string,
            response_key='dynamic_actions',
        )

    def delete(self, identifier, namespace=''):
        self._ensure_not_empty(identifier=identifier)

        self._delete(
            '/dynamic_actions/%s?namespace=%s' % (identifier, namespace)
        )
