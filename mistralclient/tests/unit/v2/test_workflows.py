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
        mock = self.mock_http_post(content={'workflows': [WORKFLOW]})

        wfs = self.workflows.create(WF_DEF)

        self.assertIsNotNone(wfs)
        self.assertEqual(WF_DEF, wfs[0].definition)

        mock.assert_called_once_with(
            URL_TEMPLATE_SCOPE,
            WF_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_update(self):
        mock = self.mock_http_put(content={'workflows': [WORKFLOW]})

        wfs = self.workflows.update(WF_DEF)

        self.assertIsNotNone(wfs)
        self.assertEqual(WF_DEF, wfs[0].definition)

        mock.assert_called_once_with(
            URL_TEMPLATE_SCOPE,
            WF_DEF,
            headers={'content-type': 'text/plain'}
        )

    def test_list(self):
        mock = self.mock_http_get(content={'workflows': [WORKFLOW]})

        workflows_list = self.workflows.list()

        self.assertEqual(1, len(workflows_list))

        wf = workflows_list[0]

        self.assertEqual(
            workflows.Workflow(self.workflows, WORKFLOW).to_dict(),
            wf.to_dict()
        )

        mock.assert_called_once_with(URL_TEMPLATE)

    def test_list_with_pagination(self):
        mock = self.mock_http_get(
            content={'workflows': [WORKFLOW], 'next': '/workflows?fake'}
        )

        workflows_list = self.workflows.list(
            limit=1,
            sort_keys='created_at',
            sort_dirs='asc'
        )

        self.assertEqual(1, len(workflows_list))

        # The url param order is unpredictable.
        self.assertIn('limit=1', mock.call_args[0][0])
        self.assertIn('sort_keys=created_at', mock.call_args[0][0])
        self.assertIn('sort_dirs=asc', mock.call_args[0][0])

    def test_get(self):
        mock = self.mock_http_get(content=WORKFLOW)

        wf = self.workflows.get('wf')

        self.assertIsNotNone(wf)
        self.assertEqual(
            workflows.Workflow(self.workflows, WORKFLOW).to_dict(),
            wf.to_dict()
        )

        mock.assert_called_once_with(URL_TEMPLATE_NAME % 'wf')

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.workflows.delete('wf')

        mock.assert_called_once_with(URL_TEMPLATE_NAME % 'wf')
