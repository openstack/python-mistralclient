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

from mistralclient.api import base
from mistralclient import utils


class Action(base.Resource):
    resource_name = 'Action'


class ActionManager(base.ResourceManager):
    resource_class = Action

    def create(self, definition, scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._create(
            '/actions?scope=%s' % scope,
            definition,
            response_key='actions',
            dump_json=False,
            headers={'content-type': 'text/plain'},
            is_iter_resp=True
        )

    def update(self, definition, scope='private', id=None):
        self._ensure_not_empty(definition=definition)

        url_pre = ('/actions/%s' % id) if id else '/actions'

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._update(
            '%s?scope=%s' % (url_pre, scope),
            definition,
            response_key='actions',
            dump_json=False,
            headers={'content-type': 'text/plain'},
            is_iter_resp=True
        )

    def list(self, marker='', limit=None, sort_keys='', sort_dirs='',
             fields='', **filters):

        query_string = self._build_query_params(
            marker=marker,
            limit=limit,
            sort_keys=sort_keys,
            sort_dirs=sort_dirs,
            fields=fields,
            filters=filters
        )

        return self._list(
            '/actions%s' % query_string,
            response_key='actions',
        )

    def get(self, identifier):
        self._ensure_not_empty(identifier=identifier)

        return self._get('/actions/%s' % identifier)

    def delete(self, identifier):
        self._ensure_not_empty(identifier=identifier)

        self._delete('/actions/%s' % identifier)

    def validate(self, definition):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        return self._validate(
            '/actions/validate',
            definition,
            dump_json=False,
            headers={'content-type': 'text/plain'}
        )
