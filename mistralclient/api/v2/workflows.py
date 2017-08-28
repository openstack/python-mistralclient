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

import six

from mistralclient.api import base
from mistralclient import utils


urlparse = six.moves.urllib.parse


class Workflow(base.Resource):
    resource_name = 'Workflow'


class WorkflowManager(base.ResourceManager):
    resource_class = Workflow

    def create(self, definition, namespace='', scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        resp = self.http_client.post(
            '/workflows?scope=%s&namespace=%s' % (scope, namespace),
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'workflows')]

    def update(self, definition, namespace='', scope='private', id=None):
        self._ensure_not_empty(definition=definition)

        url_pre = ('/workflows/%s' % id) if id else '/workflows'

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        resp = self.http_client.put(
            '%s?namespace=%s&scope=%s' % (url_pre, namespace, scope),
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        if id:
            return self.resource_class(self, base.extract_json(resp, None))

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'workflows')]

    def list(self, namespace='', marker='', limit=None, sort_keys='',
             sort_dirs='', **filters):
        qparams = {}

        if namespace:
            qparams['namespace'] = namespace

        if marker:
            qparams['marker'] = marker

        if limit:
            qparams['limit'] = limit

        if sort_keys:
            qparams['sort_keys'] = sort_keys

        if sort_dirs:
            qparams['sort_dirs'] = sort_dirs

        for name, val in filters.items():
            qparams[name] = val

        query_string = ("?%s" % urlparse.urlencode(list(qparams.items()))
                        if qparams else "")

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
        definition = utils.get_contents_if_file(definition)

        resp = self.http_client.post(
            '/workflows/validate',
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return base.extract_json(resp, None)
