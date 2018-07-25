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

from keystoneauth1 import exceptions
from mistralclient.api import base
from mistralclient import utils


class Workbook(base.Resource):
    resource_name = 'Workbook'


class WorkbookManager(base.ResourceManager):
    resource_class = Workbook

    def _get_workbooks_url(self, resource=None, namespace=None, scope=None):
        path = '/workbooks'

        if resource:
            path += '/%s' % resource

        if scope and namespace:
            path += '?scope=%s&namespace=%s' % (scope, namespace)
        elif scope:
            path += '?scope=%s' % scope
        elif namespace:
            path += '?namespace=%s' % namespace

        return path

    def create(self, definition, namespace='', scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        try:
            resp = self.http_client.post(
                self._get_workbooks_url(None, namespace, scope),
                definition,
                headers={'content-type': 'text/plain'}
            )
        except exceptions.HttpError as ex:
            self._raise_api_exception(ex.response)

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def update(self, definition, namespace='', scope='private'):
        self._ensure_not_empty(definition=definition)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(definition)

        try:
            resp = self.http_client.put(
                self._get_workbooks_url(None, namespace, scope),
                definition,
                headers={'content-type': 'text/plain'}
            )
        except exceptions.HttpError as ex:
            self._raise_api_exception(ex.response)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def list(self, namespace=''):
        return self._list(
            self._get_workbooks_url(None, namespace),
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

        try:
            resp = self.http_client.post(
                '/workbooks/validate',
                definition,
                headers={'content-type': 'text/plain'}
            )
        except exceptions.HttpError as ex:
            self._raise_api_exception(ex.response)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return base.extract_json(resp, None)
