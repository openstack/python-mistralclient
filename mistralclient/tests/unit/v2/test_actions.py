# Copyright 2015 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import pkg_resources as pkg
from six.moves.urllib import parse
from six.moves.urllib import request

from mistralclient.api import base as api_base
from mistralclient.api.v2 import actions
from mistralclient.tests.unit.v2 import base


ACTION_DEF = """
---
version: 2.0

my_action:
  base: std.echo
  base-input:
    output: 'Bye!'
  output:
    info: <% $.output %>
"""

INVALID_ACTION_DEF = """
---
version: 2.0

my_action:
  base: std.echo
  unexpected-property: 'this should fail'
  base-input:
    output: 'Bye!'
  output:
    info: <% $.output %>
"""

ACTION = {
    'id': '123',
    'name': 'my_action',
    'input': '',
    'definition': ACTION_DEF
}

URL_TEMPLATE = '/actions'
URL_TEMPLATE_SCOPE = '/actions?scope=private'
URL_TEMPLATE_NAME = '/actions/%s'
URL_TEMPLATE_VALIDATE = '/actions/validate'


class TestActionsV2(base.BaseClientV2Test):
    def test_create(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE,
                                json={'actions': [ACTION]},
                                status_code=201)

        actions = self.actions.create(ACTION_DEF)

        self.assertIsNotNone(actions)
        self.assertEqual(ACTION_DEF, actions[0].definition)

        last_request = self.requests_mock.last_request
        self.assertEqual('text/plain', last_request.headers['content-type'])
        self.assertEqual(ACTION_DEF, last_request.text)

    def test_create_with_file(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE,
                                json={'actions': [ACTION]},
                                status_code=201)

        # The contents of action_v2.yaml must be identical to ACTION_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/action_v2.yaml'
        )

        actions = self.actions.create(path)

        self.assertIsNotNone(actions)
        self.assertEqual(ACTION_DEF, actions[0].definition)

        last_request = self.requests_mock.last_request
        self.assertEqual('text/plain', last_request.headers['content-type'])
        self.assertEqual(ACTION_DEF, last_request.text)

    def test_update_with_id(self):
        self.requests_mock.put(self.TEST_URL + URL_TEMPLATE_NAME % 123,
                               json={'actions': [ACTION]})

        actions = self.actions.update(ACTION_DEF, id=123)

        self.assertIsNotNone(actions)
        self.assertEqual(ACTION_DEF, actions[0].definition)

        last_request = self.requests_mock.last_request

        self.assertEqual('scope=private', last_request.query)
        self.assertEqual('text/plain', last_request.headers['content-type'])
        self.assertEqual(ACTION_DEF, last_request.text)

    def test_update(self):
        self.requests_mock.put(self.TEST_URL + URL_TEMPLATE,
                               json={'actions': [ACTION]})

        actions = self.actions.update(ACTION_DEF)

        self.assertIsNotNone(actions)
        self.assertEqual(ACTION_DEF, actions[0].definition)

        last_request = self.requests_mock.last_request

        self.assertEqual('scope=private', last_request.query)
        self.assertEqual('text/plain', last_request.headers['content-type'])
        self.assertEqual(ACTION_DEF, last_request.text)

    def test_update_with_file_uri(self):
        self.requests_mock.put(self.TEST_URL + URL_TEMPLATE,
                               json={'actions': [ACTION]})

        # The contents of action_v2.yaml must be identical to ACTION_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/action_v2.yaml'
        )

        # Convert the file path to file URI
        uri = parse.urljoin('file:', request.pathname2url(path))

        actions = self.actions.update(uri)

        self.assertIsNotNone(actions)
        self.assertEqual(ACTION_DEF, actions[0].definition)

        last_request = self.requests_mock.last_request
        self.assertEqual('scope=private', last_request.query)
        self.assertEqual('text/plain', last_request.headers['content-type'])
        self.assertEqual(ACTION_DEF, last_request.text)

    def test_list(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'actions': [ACTION]})

        action_list = self.actions.list()

        self.assertEqual(1, len(action_list))

        action = action_list[0]

        self.assertEqual(
            actions.Action(self.actions, ACTION).to_dict(),
            action.to_dict()
        )

    def test_list_with_pagination(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'actions': [ACTION],
                                     'next': '/actions?fake'})

        action_list = self.actions.list(
            limit=1,
            sort_keys='created_at',
            sort_dirs='asc'
        )

        self.assertEqual(1, len(action_list))

        last_request = self.requests_mock.last_request

        # The url param order is unpredictable.
        self.assertEqual(['1'], last_request.qs['limit'])
        self.assertEqual(['created_at'], last_request.qs['sort_keys'])
        self.assertEqual(['asc'], last_request.qs['sort_dirs'])

    def test_get(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE_NAME % 'action',
                               json=ACTION)

        action = self.actions.get('action')

        self.assertIsNotNone(action)
        self.assertEqual(
            actions.Action(self.actions, ACTION).to_dict(),
            action.to_dict()
        )

    def test_delete(self):
        url = self.TEST_URL + URL_TEMPLATE_NAME % 'action'
        m = self.requests_mock.delete(url, status_code=204)

        self.actions.delete('action')

        self.assertEqual(1, m.call_count)

    def test_validate(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE_VALIDATE,
                                json={'valid': True})

        result = self.actions.validate(ACTION_DEF)

        self.assertIsNotNone(result)
        self.assertIn('valid', result)
        self.assertTrue(result['valid'])

        last_request = self.requests_mock.last_request
        self.assertEqual(ACTION_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_validate_with_file(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE_VALIDATE,
                                json={'valid': True})

        # The contents of action_v2.yaml must be identical to ACTION_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/action_v2.yaml'
        )

        result = self.actions.validate(path)

        self.assertIsNotNone(result)
        self.assertIn('valid', result)
        self.assertTrue(result['valid'])

        last_request = self.requests_mock.last_request
        self.assertEqual(ACTION_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_validate_failed(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE_VALIDATE,
                                json={"valid": False,
                                      "error": "mocked error message"})

        result = self.actions.validate(INVALID_ACTION_DEF)

        self.assertIsNotNone(result)
        self.assertIn('valid', result)
        self.assertFalse(result['valid'])
        self.assertIn('error', result)
        self.assertIn("mocked error message", result['error'])

        last_request = self.requests_mock.last_request
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_validate_api_failed(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE_VALIDATE,
                                status_code=500,
                                json={})

        self.assertRaises(
            api_base.APIException,
            self.actions.validate,
            ACTION_DEF
        )

        last_request = self.requests_mock.last_request

        self.assertEqual('text/plain', last_request.headers['content-type'])
        self.assertEqual(ACTION_DEF, last_request.text)
