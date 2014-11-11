# Copyright (c) 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

from mistralclient.tests.functional.cli import base


MISTRAL_URL = "http://localhost:8989/v2"


class MistralClientTestBase(base.MistralCLIAuth, base.MistralCLIAltAuth):

    _mistral_url = MISTRAL_URL

    @classmethod
    def setUpClass(cls):
        super(MistralClientTestBase, cls).setUpClass()

        cls.wb_def = os.path.relpath(
            'functionaltests/resources/v2/wb_v2.yaml', os.getcwd())

        cls.wb_with_tags_def = os.path.relpath(
            'functionaltests/resources/v2/wb_with_tags_v2.yaml', os.getcwd())

        cls.wf_def = os.path.relpath(
            'functionaltests/resources/v2/wf_v2.yaml', os.getcwd())

        cls.wf_with_delay_def = os.path.relpath(
            'functionaltests/resources/v2/wf_delay_v2.yaml', os.getcwd())

        cls.act_def = os.path.relpath(
            'functionaltests/resources/v2/action_v2.yaml', os.getcwd())

    def setUp(self):
        super(MistralClientTestBase, self).setUp()

    def get_value_of_field(self, obj, field):
        return [o['Value'] for o in obj
                if o['Field'] == "{0}".format(field)][0]

    def get_item_info(self, get_from, get_by, value):
        return [i for i in get_from if i[get_by] == value][0]

    def mistral_admin(self, cmd, params=""):
        self.clients = self._get_admin_clients()
        return self.parser.listing(self.mistral(
            '{0}'.format(cmd), params='{0}'.format(params)))

    def mistral_alt_user(self, cmd, params=""):
        self.clients = self._get_alt_clients()
        return self.parser.listing(self.mistral_alt(
            '{0}'.format(cmd), params='{0}'.format(params)))

    def mistral_cli(self, admin, cmd, params):
        if admin:
            return self.mistral_admin(cmd, params)
        else:
            return self.mistral_alt_user(cmd, params)

    def workbook_create(self, wb_def, admin=True):
        wb = self.mistral_cli(
            admin, 'workbook-create', params='{0}'.format(wb_def))
        wb_name = self.get_value_of_field(wb, "Name")
        self.addCleanup(self.mistral_cli,
                        admin, 'workbook-delete', params=wb_name)
        self.addCleanup(self.mistral_cli,
                        admin, 'workflow-delete', params='wb.wf1')

        return wb

    def workflow_create(self, wf_def, admin=True):
        wf = self.mistral_cli(
            admin, 'workflow-create', params='{0}'.format(wf_def))
        for workflow in wf:
            self.addCleanup(self.mistral_cli, admin,
                            'workflow-delete', params=workflow['Name'])

        return wf

    def action_create(self, act_def, admin=True):
        acts = self.mistral_cli(
            admin, 'action-create', params='{0}'.format(act_def))
        for action in acts:
            self.addCleanup(self.mistral_cli, admin,
                            'action-delete', params=action['Name'])

        return acts

    def cron_trigger_create(self, name, pattern,
                            wf_name, wf_input, admin=True):
        trigger = self.mistral_cli(
            admin, 'cron-trigger-create',
            params='%s "%s" %s %s' % (name, pattern, wf_name, wf_input))
        self.addCleanup(self.mistral_cli, admin,
                        'cron-trigger-delete', params=name)

        return trigger

    def execution_create(self, wf_name, admin=True):
        ex = self.mistral_cli(admin, 'execution-create', params=wf_name)
        exec_id = self.get_value_of_field(ex, 'ID')
        self.addCleanup(self.mistral_cli, admin,
                        'execution-delete', params=exec_id)

        return ex
