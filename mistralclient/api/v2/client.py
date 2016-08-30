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

import six

from oslo_utils import importutils

from mistralclient.api import httpclient
from mistralclient.api.v2 import action_executions
from mistralclient.api.v2 import actions
from mistralclient.api.v2 import cron_triggers
from mistralclient.api.v2 import environments
from mistralclient.api.v2 import executions
from mistralclient.api.v2 import members
from mistralclient.api.v2 import services
from mistralclient.api.v2 import tasks
from mistralclient.api.v2 import workbooks
from mistralclient.api.v2 import workflows
from mistralclient.auth import auth_types
from mistralclient.auth import keycloak
from mistralclient.auth import keystone

osprofiler_profiler = importutils.try_import("osprofiler.profiler")

_DEFAULT_MISTRAL_URL = "http://localhost:8989/v2"


class Client(object):
    def __init__(self, mistral_url=None, username=None, api_key=None,
                 project_name=None, auth_url=None, project_id=None,
                 endpoint_type='publicURL', service_type='workflowv2',
                 auth_token=None, user_id=None, cacert=None, insecure=False,
                 profile=None, auth_type=auth_types.KEYSTONE, client_id=None,
                 client_secret=None, target_username=None, target_api_key=None,
                 target_project_name=None, target_auth_url=None,
                 target_project_id=None, target_auth_token=None,
                 target_user_id=None, target_cacert=None,
                 target_insecure=False, **kwargs):

        if mistral_url and not isinstance(mistral_url, six.string_types):
            raise RuntimeError('Mistral url should be a string.')

        if auth_url:
            if auth_type == auth_types.KEYSTONE:
                (mistral_url, auth_token, project_id, user_id) = (
                    keystone.authenticate(
                        mistral_url,
                        username,
                        api_key,
                        project_name,
                        auth_url,
                        project_id,
                        endpoint_type,
                        service_type,
                        auth_token,
                        user_id,
                        cacert,
                        insecure
                    )
                )
            elif auth_type == auth_types.KEYCLOAK_OIDC:
                auth_token = keycloak.authenticate(
                    auth_url,
                    client_id,
                    client_secret,
                    project_name,
                    username,
                    api_key,
                    auth_token,
                    cacert,
                    insecure
                )

                # In case of KeyCloak OpenID Connect we can treat project
                # name and id in the same way because KeyCloak realm is
                # essentially a different OpenID Connect Issuer which in
                # KeyCloak is represented just as a URL path component
                # (see http://openid.net/specs/openid-connect-core-1_0.html).
                project_id = project_name
            else:
                raise RuntimeError(
                    'Invalid authentication type [value=%s, valid_values=%s]'
                    % (auth_type, auth_types.ALL)
                )

        if not mistral_url:
            mistral_url = _DEFAULT_MISTRAL_URL

        if profile:
            osprofiler_profiler.init(profile)

        if target_auth_url:
            keystone.authenticate(
                mistral_url,
                target_username,
                target_api_key,
                target_project_name,
                target_auth_url,
                target_project_id,
                endpoint_type,
                service_type,
                target_auth_token,
                target_user_id,
                target_cacert,
                target_insecure
            )

        self.http_client = httpclient.HTTPClient(
            mistral_url,
            auth_token,
            project_id,
            user_id,
            cacert=cacert,
            insecure=insecure,
            target_token=target_auth_token,
            target_auth_uri=target_auth_url,
            **kwargs
        )

        # Create all resource managers.
        self.workbooks = workbooks.WorkbookManager(self)
        self.executions = executions.ExecutionManager(self)
        self.tasks = tasks.TaskManager(self)
        self.actions = actions.ActionManager(self)
        self.workflows = workflows.WorkflowManager(self)
        self.cron_triggers = cron_triggers.CronTriggerManager(self)
        self.environments = environments.EnvironmentManager(self)
        self.action_executions = action_executions.ActionExecutionManager(self)
        self.services = services.ServiceManager(self)
        self.members = members.MemberManager(self)
