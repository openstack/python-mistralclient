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

import copy
import datetime
import os
import tempfile
from unittest import mock

from oslo_serialization import jsonutils

import yaml

from mistralclient.api.v2 import environments
from mistralclient.commands.v2 import environments as environment_cmd
from mistralclient.tests.unit import base


ENVIRONMENT_DICT = {
    'name': 'env1',
    'description': 'Test Environment #1',
    'scope': 'private',
    'variables': {
        'server': 'localhost',
        'database': 'test',
        'timeout': 600,
        'verbose': True
    },
    'created_at': str(datetime.datetime.utcnow()),
    'updated_at': str(datetime.datetime.utcnow())
}

ENVIRONMENT = environments.Environment(mock, ENVIRONMENT_DICT)
EXPECTED_RESULT = (ENVIRONMENT_DICT['name'],
                   ENVIRONMENT_DICT['description'],
                   jsonutils.dumps(ENVIRONMENT_DICT['variables'], indent=4),
                   ENVIRONMENT_DICT['scope'],
                   ENVIRONMENT_DICT['created_at'],
                   ENVIRONMENT_DICT['updated_at'])

EXPECTED_EXPORT_RESULT = (ENVIRONMENT_DICT['name'],
                          ENVIRONMENT_DICT['description'],
                          ENVIRONMENT_DICT['scope'],
                          jsonutils.dumps(ENVIRONMENT_DICT['variables']))


class TestCLIEnvironmentsV2(base.BaseCommandTest):

    def _test_create(self, content):
        self.client.environments.create.return_value = ENVIRONMENT

        with tempfile.NamedTemporaryFile() as f:
            f.write(content.encode('utf-8'))
            f.flush()
            file_path = os.path.abspath(f.name)
            result = self.call(environment_cmd.Create, app_args=[file_path])
            self.assertEqual(EXPECTED_RESULT, result[1])

    def test_create_from_json(self):
        self._test_create(jsonutils.dumps(ENVIRONMENT_DICT, indent=4))

    def test_create_from_yaml(self):
        yml = yaml.dump(ENVIRONMENT_DICT, default_flow_style=False)
        self._test_create(yml)

    def _test_update(self, content):
        self.client.environments.update.return_value = ENVIRONMENT

        with tempfile.NamedTemporaryFile() as f:
            f.write(content.encode('utf-8'))
            f.flush()
            file_path = os.path.abspath(f.name)
            result = self.call(environment_cmd.Update, app_args=[file_path])
            self.assertEqual(EXPECTED_RESULT, result[1])

    def test_update_from_json(self):
        env = copy.deepcopy(ENVIRONMENT_DICT)
        del env['created_at']
        del env['updated_at']
        self._test_update(jsonutils.dumps(env, indent=4))

    def test_update_from_yaml(self):
        env = copy.deepcopy(ENVIRONMENT_DICT)
        del env['created_at']
        del env['updated_at']
        yml = yaml.dump(env, default_flow_style=False)
        self._test_update(yml)

    def test_list(self):
        self.client.environments.list.return_value = [ENVIRONMENT]
        expected = (ENVIRONMENT_DICT['name'],
                    ENVIRONMENT_DICT['description'],
                    ENVIRONMENT_DICT['scope'],
                    ENVIRONMENT_DICT['created_at'],
                    ENVIRONMENT_DICT['updated_at'])

        result = self.call(environment_cmd.List)

        self.assertListEqual([expected], result[1])

    def test_get(self):
        self.client.environments.get.return_value = ENVIRONMENT

        result = self.call(environment_cmd.Get, app_args=['name'])

        self.assertEqual(EXPECTED_RESULT, result[1])

    def test_get_with_export(self):
        self.client.environments.get.return_value = ENVIRONMENT

        result = self.call(environment_cmd.Get, app_args=['--export', 'name'])

        self.assertEqual(EXPECTED_EXPORT_RESULT, result[1])

    def test_delete(self):
        self.call(environment_cmd.Delete, app_args=['name'])

        self.client.environments.delete.assert_called_once_with('name')

    def test_delete_with_multi_names(self):
        self.call(environment_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, self.client.environments.delete.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            self.client.environments.delete.call_args_list
        )
