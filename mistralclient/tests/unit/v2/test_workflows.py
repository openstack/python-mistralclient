# Copyright 2015 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
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

from mistralclient.api.v2 import workflows
from mistralclient.tests.unit.v2 import base


WF_DEF = """
---
version: 2.0

my_wf:
  type: direct

  tasks:
    task1:
      action: std.echo output="hello, world"
"""

WORKFLOW = {
    'id': '123',
    'name': 'my_wf',
    'input': '',
    'definition': WF_DEF
}

URL_TEMPLATE = '/workflows'
URL_TEMPLATE_SCOPE = '/workflows?scope=private'
URL_TEMPLATE_NAME = '/workflows/%s'


class TestWorkflowsV2(base.BaseClientV2Test):
    def test_create(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE_SCOPE,
                                json={'workflows': [WORKFLOW]},
                                status_code=201)

        wfs = self.workflows.create(WF_DEF)

        self.assertIsNotNone(wfs)
        self.assertEqual(WF_DEF, wfs[0].definition)

        last_request = self.requests_mock.last_request

        self.assertEqual(WF_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_create_with_file(self):
        self.requests_mock.post(self.TEST_URL + URL_TEMPLATE_SCOPE,
                                json={'workflows': [WORKFLOW]},
                                status_code=201)

        # The contents of wf_v2.yaml must be identical to WF_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/wf_v2.yaml'
        )

        wfs = self.workflows.create(path)

        self.assertIsNotNone(wfs)
        self.assertEqual(WF_DEF, wfs[0].definition)

        last_request = self.requests_mock.last_request

        self.assertEqual(WF_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_update(self):
        self.requests_mock.put(self.TEST_URL + URL_TEMPLATE_SCOPE,
                               json={'workflows': [WORKFLOW]})

        wfs = self.workflows.update(WF_DEF)

        self.assertIsNotNone(wfs)
        self.assertEqual(WF_DEF, wfs[0].definition)

        last_request = self.requests_mock.last_request

        self.assertEqual(WF_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_update_with_id(self):
        self.requests_mock.put(self.TEST_URL + URL_TEMPLATE_NAME % '123',
                               json=WORKFLOW)

        wf = self.workflows.update(WF_DEF, id='123')

        self.assertIsNotNone(wf)
        self.assertEqual(WF_DEF, wf.definition)

        last_request = self.requests_mock.last_request

        self.assertEqual('namespace=&scope=private', last_request.query)
        self.assertEqual(WF_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_update_with_file_uri(self):
        self.requests_mock.put(self.TEST_URL + URL_TEMPLATE_SCOPE,
                               json={'workflows': [WORKFLOW]})

        # The contents of wf_v2.yaml must be identical to WF_DEF
        path = pkg.resource_filename(
            'mistralclient',
            'tests/unit/resources/wf_v2.yaml'
        )

        # Convert the file path to file URI
        uri = parse.urljoin('file:', request.pathname2url(path))

        wfs = self.workflows.update(uri)

        self.assertIsNotNone(wfs)
        self.assertEqual(WF_DEF, wfs[0].definition)

        last_request = self.requests_mock.last_request

        self.assertEqual(WF_DEF, last_request.text)
        self.assertEqual('text/plain', last_request.headers['content-type'])

    def test_list(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'workflows': [WORKFLOW]})

        workflows_list = self.workflows.list()

        self.assertEqual(1, len(workflows_list))

        wf = workflows_list[0]

        self.assertEqual(
            workflows.Workflow(self.workflows, WORKFLOW).to_dict(),
            wf.to_dict()
        )

    def test_list_with_pagination(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'workflows': [WORKFLOW],
                                     'next': '/workflows?fake'})

        workflows_list = self.workflows.list(
            limit=1,
            sort_keys='created_at',
            sort_dirs='asc'
        )

        self.assertEqual(1, len(workflows_list))

        last_request = self.requests_mock.last_request

        # The url param order is unpredictable.
        self.assertEqual(['1'], last_request.qs['limit'])
        self.assertEqual(['created_at'], last_request.qs['sort_keys'])
        self.assertEqual(['asc'], last_request.qs['sort_dirs'])

    def test_list_with_no_limit(self):
        self.requests_mock.get(self.TEST_URL + URL_TEMPLATE,
                               json={'workflows': [WORKFLOW]})

        workflows_list = self.workflows.list(limit=-1)

        self.assertEqual(1, len(workflows_list))

        last_request = self.requests_mock.last_request

        self.assertNotIn('limit', last_request.qs)

    def test_get(self):
        url = self.TEST_URL + URL_TEMPLATE_NAME % 'wf'
        self.requests_mock.get(url, json=WORKFLOW)

        wf = self.workflows.get('wf')

        self.assertIsNotNone(wf)
        self.assertEqual(
            workflows.Workflow(self.workflows, WORKFLOW).to_dict(),
            wf.to_dict()
        )

    def test_delete(self):
        url = self.TEST_URL + URL_TEMPLATE_NAME % 'wf'
        self.requests_mock.delete(url, status_code=204)

        self.workflows.delete('wf')
