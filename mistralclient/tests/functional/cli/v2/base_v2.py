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
import time

from tempest.lib import exceptions

from mistralclient.tests.functional.cli import base


MISTRAL_URL = "http://localhost:8989/v2"


class MistralClientTestBase(base.MistralCLIAuth, base.MistralCLIAltAuth):

    _mistral_url = MISTRAL_URL

    @classmethod
    def setUpClass(cls):
        super(MistralClientTestBase, cls).setUpClass()

        cls.wb_def = os.path.relpath(
            'functionaltests/resources/v2/wb_v2.yaml', os.getcwd()
        )

        cls.wb_with_tags_def = os.path.relpath(
            'functionaltests/resources/v2/wb_with_tags_v2.yaml', os.getcwd()
        )

        cls.wf_def = os.path.relpath(
            'functionaltests/resources/v2/wf_v2.yaml', os.getcwd()
        )

        cls.wf_single_def = os.path.relpath(
            'functionaltests/resources/v2/wf_single_v2.yaml', os.getcwd()
        )

        cls.wf_with_delay_def = os.path.relpath(
            'functionaltests/resources/v2/wf_delay_v2.yaml', os.getcwd()
        )

        cls.act_def = os.path.relpath(
            'functionaltests/resources/v2/action_v2.yaml', os.getcwd()
        )

        cls.act_tag_def = os.path.relpath(
            'functionaltests/resources/v2/action_v2_tags.yaml', os.getcwd()
        )

    def setUp(self):
        super(MistralClientTestBase, self).setUp()

    def get_field_value(self, obj, field):
        return [
            o['Value'] for o in obj
            if o['Field'] == "{0}".format(field)
        ][0]

    def get_item_info(self, get_from, get_by, value):
        return [i for i in get_from if i[get_by] == value][0]

    def mistral_admin(self, cmd, params=""):
        self.clients = self._get_admin_clients()

        return self.parser.listing(
            self.mistral('{0}'.format(cmd), params='{0}'.format(params))
        )

    def mistral_alt_user(self, cmd, params=""):
        self.clients = self._get_alt_clients()

        return self.parser.listing(
            self.mistral_alt('{0}'.format(cmd), params='{0}'.format(params))
        )

    def mistral_cli(self, admin, cmd, params=''):
        if admin:
            return self.mistral_admin(cmd, params)
        else:
            return self.mistral_alt_user(cmd, params)

    def workbook_create(self, wb_def, admin=True):
        wb = self.mistral_cli(
            admin,
            'workbook-create',
            params='{0}'.format(wb_def)
        )

        wb_name = self.get_field_value(wb, "Name")

        self.addCleanup(
            self.mistral_cli,
            admin,
            'workbook-delete',
            params=wb_name
        )

        self.addCleanup(
            self.mistral_cli,
            admin,
            'workflow-delete',
            params='wb.wf1'
        )

        return wb

    def workflow_create(self, wf_def, admin=True, scope='private'):
        params = '{0}'.format(wf_def)

        if scope == 'public':
            params += ' --public'

        wf = self.mistral_cli(
            admin,
            'workflow-create',
            params=params
        )

        for workflow in wf:
            self.addCleanup(
                self.mistral_cli,
                admin,
                'workflow-delete',
                params=workflow['ID']
            )

        return wf

    def workflow_member_create(self, wf_id):
        cmd_param = (
            '%s workflow %s' % (wf_id, self.get_project_id("demo"))
        )
        member = self.mistral_admin("member-create", params=cmd_param)

        self.addCleanup(
            self.mistral_admin,
            'member-delete',
            params=cmd_param
        )

        return member

    def action_create(self, act_def, admin=True, scope='private'):
        params = '{0}'.format(act_def)

        if scope == 'public':
            params += ' --public'

        acts = self.mistral_cli(
            admin,
            'action-create',
            params=params
        )

        for action in acts:
            self.addCleanup(
                self.mistral_cli,
                admin,
                'action-delete',
                params=action['Name']
            )

        return acts

    def cron_trigger_create(self, name, wf_name, wf_input, pattern=None,
                            count=None, first_time=None, admin=True):
        optional_params = ""

        if pattern:
            optional_params += ' --pattern "{}"'.format(pattern)
        if count:
            optional_params += ' --count {}'.format(count)
        if first_time:
            optional_params += ' --first-time "{}"'.format(first_time)

        trigger = self.mistral_cli(
            admin,
            'cron-trigger-create',
            params='{} {} {} {}'.format(name, wf_name, wf_input,
                                        optional_params))

        self.addCleanup(self.mistral_cli,
                        admin,
                        'cron-trigger-delete',
                        params=name)

        return trigger

    def execution_create(self, params, admin=True):
        ex = self.mistral_cli(admin, 'execution-create', params=params)
        exec_id = self.get_field_value(ex, 'ID')

        self.addCleanup(
            self.mistral_cli,
            admin,
            'execution-delete',
            params=exec_id
        )

        return ex

    def environment_create(self, params, admin=True):
        env = self.mistral_cli(admin, 'environment-create', params=params)
        env_name = self.get_field_value(env, 'Name')

        self.addCleanup(
            self.mistral_cli,
            admin,
            'environment-delete',
            params=env_name
        )

        return env

    def create_file(self, file_name, file_body=""):
        f = open(file_name, 'w')
        f.write(file_body)
        f.close()

        self.addCleanup(os.remove, file_name)

    def wait_execution_success(self, exec_id, timeout=180):
        start_time = time.time()

        ex = self.mistral_admin('execution-get', params=exec_id)
        exec_state = self.get_field_value(ex, 'State')

        expected_states = ['SUCCESS', 'RUNNING']

        while exec_state != 'SUCCESS':
            if time.time() - start_time > timeout:
                msg = ("Execution exceeds timeout {0} to change state "
                       "to SUCCESS. Execution: {1}".format(timeout, ex))

                raise exceptions.TimeoutException(msg)

            ex = self.mistral_admin('execution-get', params=exec_id)
            exec_state = self.get_field_value(ex, 'State')

            if exec_state not in expected_states:
                msg = ("Execution state %s is not in expected "
                       "states: %s" % (exec_state, expected_states))

                raise exceptions.TempestException(msg)

            time.sleep(2)

        return True
