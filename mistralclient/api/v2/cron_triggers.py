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

import json

from mistralclient.api import base


class CronTrigger(base.Resource):
    resource_name = 'CronTrigger'


class CronTriggerManager(base.ResourceManager):
    resource_class = CronTrigger

    def create(self, name, workflow_name, workflow_input=None,
               workflow_params=None, pattern=None,
               first_time=None, count=None):
        self._ensure_not_empty(
            name=name,
            workflow_name=workflow_name
        )

        data = {
            'name': name,
            'workflow_name': workflow_name,
            'pattern': pattern,
            'first_execution_time': first_time,
            'remaining_executions': count
        }

        if workflow_input:
            data.update({'workflow_input': json.dumps(workflow_input)})

        if workflow_params:
            data.update({'workflow_params': json.dumps(workflow_params)})

        return self._create('/cron_triggers', data)

    def list(self):
        return self._list('/cron_triggers', response_key='cron_triggers')

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/cron_triggers/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/cron_triggers/%s' % name)
