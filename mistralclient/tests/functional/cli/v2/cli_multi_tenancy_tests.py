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

from tempest_lib import exceptions

from mistralclient.tests.functional.cli.v2 import base_v2


class StandardItemsAvailabilityCLITests(base_v2.MistralClientTestBase):

    def test_std_workflows_availability(self):
        wfs = self.mistral_admin("workflow-list")

        self.assertTableStruct(
            wfs,
            ["Name", "Tags", "Input", "Created at", "Updated at"]
        )
        self.assertIn("std.create_instance",
                      [workflow["Name"] for workflow in wfs])

        wfs = self.mistral_alt_user("workflow-list")

        self.assertTableStruct(
            wfs,
            ["Name", "Tags", "Input", "Created at", "Updated at"]
        )
        self.assertIn("std.create_instance",
                      [workflow["Name"] for workflow in wfs])

    def test_std_actions_availability(self):
        acts = self.mistral_admin("action-list")

        self.assertTableStruct(
            acts,
            ["Name", "Is system", "Input", "Description",
             "Tags", "Created at", "Updated at"]
        )
        self.assertIn("glance.images_list",
                      [action["Name"] for action in acts])

        acts = self.mistral_alt_user("action-list")

        self.assertTableStruct(
            acts,
            ["Name", "Is system", "Input", "Description",
             "Tags", "Created at", "Updated at"]
        )
        self.assertIn("glance.images_list",
                      [action["Name"] for action in acts])


class WorkbookIsolationCLITests(base_v2.MistralClientTestBase):

    def test_workbook_name_uniqueness(self):
        self.workbook_create(self.wb_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            "workbook-create",
            params="{0}".format(self.wb_def)
        )

        self.workbook_create(self.wb_def, admin=False)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "workbook-create",
            params="{0}".format(self.wb_def)
        )

    def test_wb_isolation(self):
        wb = self.workbook_create(self.wb_def)
        wb_name = self.get_value_of_field(wb, "Name")
        wbs = self.mistral_admin("workbook-list")

        self.assertIn(wb_name, [w["Name"] for w in wbs])

        alt_wbs = self.mistral_alt_user("workbook-list")

        self.assertNotIn(wb_name, [w["Name"] for w in alt_wbs])

    def test_get_wb_from_another_tenant(self):
        wb = self.workbook_create(self.wb_def)
        name = self.get_value_of_field(wb, "Name")

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "workbook-get",
            params=name
        )

    def test_delete_wb_from_another_tenant(self):
        wb = self.workbook_create(self.wb_def)
        name = self.get_value_of_field(wb, "Name")

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "workbook-delete",
            params=name
        )


class WorkflowIsolationCLITests(base_v2.MistralClientTestBase):

    def test_workflow_name_uniqueness(self):
        self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            "workflow-create",
            params="{0}".format(self.wf_def)
        )

        self.workflow_create(self.wf_def, admin=False)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "workflow-create",
            params="{0}".format(self.wf_def)
        )

    def test_wf_isolation(self):
        wf = self.workflow_create(self.wf_def)
        wfs = self.mistral_admin("workflow-list")

        self.assertIn(wf[0]["Name"], [w["Name"] for w in wfs])

        alt_wfs = self.mistral_alt_user("workflow-list")

        self.assertNotIn(wf[0]["Name"], [w["Name"] for w in alt_wfs])

    def test_get_wf_from_another_tenant(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "workflow-get",
            params=wf[0]["Name"]
        )

    def test_delete_wf_from_another_tenant(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "workflow-delete",
            params=wf[0]["Name"]
        )


class ActionIsolationCLITests(base_v2.MistralClientTestBase):

    def test_actions_name_uniqueness(self):
        self.action_create(self.act_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            "action-create",
            params="{0}".format(self.act_def)
        )

        self.action_create(self.act_def, admin=False)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "action-create",
            params="{0}".format(self.act_def)
        )

    def test_action_isolation(self):
        act = self.action_create(self.act_def)
        acts = self.mistral_admin("action-list")

        self.assertIn(act[0]["Name"], [a["Name"] for a in acts])

        alt_acts = self.mistral_alt_user("action-list")

        self.assertNotIn(act[0]["Name"], [a["Name"] for a in alt_acts])

    def test_get_action_from_another_tenant(self):
        act = self.action_create(self.act_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "action-get",
            params=act[0]["Name"]
        )

    def test_delete_action_from_another_tenant(self):
        act = self.action_create(self.act_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "action-delete",
            params=act[0]["Name"]
        )


class CronTriggerIsolationCLITests(base_v2.MistralClientTestBase):

    def test_cron_trigger_name_uniqueness(self):
        wf = self.workflow_create(self.wf_def)
        self.cron_trigger_create(
            "trigger", "5 * * * *", wf[0]["Name"], "{}")

        self.assertRaises(
            exceptions.CommandFailed,
            self.cron_trigger_create,
            "trigger",
            "5 * * * *",
            wf[0]["Name"],
            "{}"
        )

        wf = self.workflow_create(self.wf_def, admin=False)
        self.cron_trigger_create(
            "trigger", "5 * * * *", wf[0]["Name"], "{}", admin=False)

        self.assertRaises(
            exceptions.CommandFailed,
            self.cron_trigger_create,
            "trigger",
            "5 * * * *",
            wf[0]["Name"],
            "{}",
            admin=False
        )

    def test_cron_trigger_isolation(self):
        wf = self.workflow_create(self.wf_def)
        self.cron_trigger_create(
            "trigger", "5 * * * *", wf[0]["Name"], "{}")

        alt_trs = self.mistral_alt_user("cron-trigger-list")

        self.assertNotIn("trigger", [t["Name"] for t in alt_trs])


class ExecutionIsolationCLITests(base_v2.MistralClientTestBase):

    def test_execution_isolation(self):
        wf = self.workflow_create(self.wf_def)
        ex = self.execution_create(wf[0]["Name"])
        exec_id = self.get_value_of_field(ex, "ID")

        execs = self.mistral_admin("execution-list")
        self.assertIn(exec_id, [e["ID"] for e in execs])

        alt_execs = self.mistral_alt_user("execution-list")
        self.assertNotIn(exec_id, [e["ID"] for e in alt_execs])

    def test_get_execution_from_another_tenant(self):
        wf = self.workflow_create(self.wf_def)
        ex = self.execution_create(wf[0]["Name"])
        exec_id = self.get_value_of_field(ex, "ID")

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "execution-get",
            params=exec_id
        )


class EnvironmentIsolationCLITests(base_v2.MistralClientTestBase):

    def setUp(self):
        super(EnvironmentIsolationCLITests, self).setUp()

        self.env_file = "env.yaml"
        self.create_file("{0}".format(self.env_file),
                         "name: env\n"
                         "description: Test env\n"
                         "variables:\n"
                         "  var: value")

    def test_environment_name_uniqueness(self):
        self.environment_create(self.env_file)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            "environment-create",
            params=self.env_file
        )

        self.environment_create(self.env_file, admin=False)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "environment-create",
            params=self.env_file
        )

    def test_environment_isolation(self):
        env = self.environment_create(self.env_file)
        env_name = self.get_value_of_field(env, "Name")
        envs = self.mistral_admin("environment-list")

        self.assertIn(env_name, [en["Name"] for en in envs])

        alt_envs = self.mistral_alt_user("environment-list")

        self.assertNotIn(env_name, [en["Name"] for en in alt_envs])

    def test_get_env_from_another_tenant(self):
        env = self.environment_create(self.env_file)
        env_name = self.get_value_of_field(env, "Name")

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "environment-get",
            params=env_name
        )

    def test_delete_env_from_another_tenant(self):
        env = self.environment_create(self.env_file)
        env_name = self.get_value_of_field(env, "Name")

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_alt_user,
            "environment-delete",
            params=env_name
        )
