# Copyright 2017, OpenStack Foundation
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

from oslo_serialization import jsonutils

from mistralclient.api import base


class EventTrigger(base.Resource):
    resource_name = 'EventTrigger'


class EventTriggerManager(base.ResourceManager):
    resource_class = EventTrigger

    def create(self, name, workflow_id, exchange, topic, event,
               workflow_input=None, workflow_params=None):
        self._ensure_not_empty(
            name=name,
            workflow_id=workflow_id
        )

        data = {
            'workflow_id': workflow_id,
            'name': name,
            'exchange': exchange,
            'topic': topic,
            'event': event
        }

        if workflow_input:
            data.update({'workflow_input': jsonutils.dumps(workflow_input)})

        if workflow_params:
            data.update({'workflow_params': jsonutils.dumps(workflow_params)})

        return self._create('/event_triggers', data)

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

        return self._list('/event_triggers%s' % query_string,
                          response_key='event_triggers')

    def get(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/event_triggers/%s' % id)

    def delete(self, id):
        self._ensure_not_empty(id=id)

        self._delete('/event_triggers/%s' % id)
