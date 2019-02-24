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

from oslo_serialization import jsonutils

from mistralclient.api import base
from mistralclient import utils


class Environment(base.Resource):
    resource_name = 'Environment'

    def _set_attributes(self):
        """Override loading of the "variables" attribute from text to dict."""
        for k, v in self._data.items():
            if k == 'variables' and isinstance(v, six.string_types):
                v = jsonutils.loads(v)

            try:
                setattr(self, k, v)
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass


class EnvironmentManager(base.ResourceManager):
    resource_class = Environment

    def create(self, **kwargs):
        # Check to see if the file name or URI is being passed in. If so,
        # read it's contents first.
        if 'file' in kwargs:
            file = kwargs['file']
            kwargs = utils.load_content(utils.get_contents_if_file(file))

        self._ensure_not_empty(name=kwargs.get('name', None),
                               variables=kwargs.get('variables', None))

        # Convert dict to text for the variables attribute.
        if isinstance(kwargs['variables'], dict):
            kwargs['variables'] = jsonutils.dumps(kwargs['variables'])

        return self._create('/environments', kwargs)

    def update(self, **kwargs):
        # Check to see if the file name or URI is being passed in. If so,
        # read it's contents first.
        if 'file' in kwargs:
            file = kwargs['file']
            kwargs = utils.load_content(utils.get_contents_if_file(file))

        name = kwargs.get('name', None)
        self._ensure_not_empty(name=name)

        # Convert dict to text for the variables attribute.
        if kwargs.get('variables') and isinstance(kwargs['variables'], dict):
            kwargs['variables'] = jsonutils.dumps(kwargs['variables'])

        return self._update('/environments', kwargs)

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

        return self._list('/environments%s' % query_string,
                          response_key='environments')

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/environments/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/environments/%s' % name)
