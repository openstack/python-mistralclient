# Copyright 2014 - Mirantis, Inc.
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
import six

from oslo_utils import importutils

from mistralclient.api import httpclient
from mistralclient.api.v2 import action_executions
from mistralclient.api.v2 import actions
from mistralclient.api.v2 import cron_triggers
from mistralclient.api.v2 import environments
from mistralclient.api.v2 import event_triggers
from mistralclient.api.v2 import executions
from mistralclient.api.v2 import members
from mistralclient.api.v2 import services
from mistralclient.api.v2 import tasks
from mistralclient.api.v2 import workbooks
from mistralclient.api.v2 import workflows
from mistralclient import auth


osprofiler_profiler = importutils.try_import("osprofiler.profiler")

_DEFAULT_MISTRAL_URL = "http://localhost:8989/v2"


class Client(object):

    def __init__(self, auth_type='keystone', **kwargs):
        # We get the session at this point, as some instances of session
        # objects might have mutexes that can't be deep-copied.
        session = kwargs.pop('session', None)
        req = copy.deepcopy(kwargs)
        mistral_url = req.get('mistral_url')
        profile = req.get('profile')

        if mistral_url and not isinstance(mistral_url, six.string_types):
            raise RuntimeError('Mistral url should be a string.')

        auth_handler = auth.get_auth_handler(auth_type)
        auth_response = auth_handler.authenticate(req, session=session) or {}

        # If the session was None and we're using keystone auth, it will be
        # created by the auth_handler.
        session = auth_response.pop('session', None)

        req.update(auth_response)

        mistral_url = auth_response.get('mistral_url') or mistral_url

        if not mistral_url:
            mistral_url = _DEFAULT_MISTRAL_URL

        if profile:
            osprofiler_profiler.init(profile)

        http_client = httpclient.HTTPClient(mistral_url, session=session,
                                            **req)

        # Create all resource managers.
        self.workbooks = workbooks.WorkbookManager(http_client)
        self.executions = executions.ExecutionManager(http_client)
        self.tasks = tasks.TaskManager(http_client)
        self.actions = actions.ActionManager(http_client)
        self.workflows = workflows.WorkflowManager(http_client)
        self.cron_triggers = cron_triggers.CronTriggerManager(http_client)
        self.event_triggers = event_triggers.EventTriggerManager(http_client)
        self.environments = environments.EnvironmentManager(http_client)
        self.action_executions = action_executions.ActionExecutionManager(
            http_client)
        self.services = services.ServiceManager(http_client)
        self.members = members.MemberManager(http_client)
