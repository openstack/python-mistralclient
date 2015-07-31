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

from mistralclient.api import base


class Environment(base.Resource):
    resource_name = 'Environment'

    def _set_attributes(self):
        """Override loading of the "variables" attribute from text to dict."""
        for k, v in self._data.items():
            if k == 'variables' and isinstance(v, six.string_types):
                v = json.loads(v)

            try:
                setattr(self, k, v)
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass


class EnvironmentManager(base.ResourceManager):
    resource_class = Environment

    def create(self, **kwargs):
        self._ensure_not_empty(name=kwargs.get('name', None),
                               variables=kwargs.get('variables', None))

        # Convert dict to text for the variables attribute.
        if isinstance(kwargs['variables'], dict):
            kwargs['variables'] = json.dumps(kwargs['variables'])

        return self._create('/environments', kwargs)

    def update(self, **kwargs):
        name = kwargs.get('name', None)
        self._ensure_not_empty(name=name)

        # Convert dict to text for the variables attribute.
        if kwargs.get('variables') and isinstance(kwargs['variables'], dict):
            kwargs['variables'] = json.dumps(kwargs['variables'])

        return self._update('/environments', kwargs)

    def list(self):
        return self._list('/environments', response_key='environments')

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/environments/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/environments/%s' % name)
