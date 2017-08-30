# Copyright 2016 - Nokia Networks
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

import logging

import keystoneauth1.identity.generic as auth_plugin
from keystoneauth1 import session as ks_session
import mistralclient.api.httpclient as api
from mistralclient import auth as mistral_auth
from oslo_serialization import jsonutils


LOG = logging.getLogger(__name__)


class KeystoneAuthHandler(mistral_auth.AuthHandler):

    def authenticate(self, req, session=None):
        """Performs authentication via Keystone.

        :param req: Request dict containing list of parameters required
            for Keystone authentication.

        """
        if not isinstance(req, dict):
            raise TypeError('The input "req" is not typeof dict.')

        session = session
        mistral_url = req.get('mistral_url')
        endpoint_type = req.get('endpoint_type', 'publicURL')
        service_type = req.get('service_type', 'workflowv2')

        auth_url = req.get('auth_url')
        username = req.get('username')
        user_id = req.get('user_id')
        api_key = req.get('api_key')
        auth_token = req.get('auth_token')
        project_name = req.get('project_name')
        project_id = req.get('project_id')
        region_name = req.get('region_name')
        user_domain_name = req.get('user_domain_name')
        user_domain_id = req.get('user_domain_id')
        project_domain_name = req.get('project_domain_name')
        project_domain_id = req.get('project_domain_id')
        cacert = req.get('cacert')
        insecure = req.get('insecure', False)
        target_auth_url = req.get('target_auth_url')
        target_username = req.get('target_username')
        target_user_id = req.get('target_user_id')
        target_api_key = req.get('target_api_key')
        target_auth_token = req.get('target_auth_token')
        target_project_name = req.get('target_project_name')
        target_project_id = req.get('target_project_id')
        target_user_domain_name = req.get('target_user_domain_name')
        target_user_domain_id = req.get('target_user_domain_id')
        target_project_domain_name = req.get('target_project_domain_name')
        target_project_domain_id = req.get('target_project_domain_id')
        target_cacert = req.get('target_cacert')
        target_insecure = req.get('target_insecure')

        if project_name and project_id:
            raise RuntimeError(
                'Only project name or project id should be set'
            )

        if username and user_id:
            raise RuntimeError(
                'Only user name or user id should be set'
            )

        auth_response = {}

        if not session:
            auth = None
            if auth_token:
                auth = auth_plugin.Token(
                    auth_url=auth_url,
                    token=auth_token,
                    project_id=project_id,
                    project_name=project_name,
                    project_domain_name=project_domain_name,
                    project_domain_id=project_domain_id,
                    cacert=cacert,
                    insecure=insecure)
            elif api_key and (username or user_id):
                auth = auth_plugin.Password(
                    auth_url=auth_url,
                    username=username,
                    user_id=user_id,
                    password=api_key,
                    user_domain_name=user_domain_name,
                    user_domain_id=user_domain_id,
                    project_id=project_id,
                    project_name=project_name,
                    project_domain_name=project_domain_name,
                    project_domain_id=project_domain_id)

            else:
                # NOTE(jaosorior): We don't crash here cause it's needed for
                # bash-completion to work. However, we do issue a warning to
                # the user so if the request doesn't work. It's because of
                # this.
                LOG.warning("You must either provide a valid token or "
                            "a password (api_key) and a user.")
            if auth:
                session = ks_session.Session(auth=auth)

        if session:
            if not mistral_url:
                try:
                    mistral_url = session.get_endpoint(
                        service_type=service_type,
                        endpoint_type=endpoint_type,
                        region_name=region_name
                    )
                except Exception:
                    mistral_url = None

            auth_response['mistral_url'] = mistral_url
            auth_response['session'] = session

        if target_auth_url:
            if target_auth_token:
                target_auth = auth_plugin.Token(
                    auth_url=target_auth_url,
                    token=target_auth_token,
                    project_id=target_project_id,
                    project_name=target_project_name,
                    project_domain_name=target_project_domain_name,
                    project_domain_id=target_project_domain_id,
                    cacert=target_cacert,
                    insecure=target_insecure)
            elif target_api_key and (target_username or target_user_id):
                target_auth = auth_plugin.Password(
                    auth_url=target_auth_url,
                    username=target_username,
                    user_id=target_user_id,
                    password=target_api_key,
                    user_domain_name=target_user_domain_name,
                    user_domain_id=target_user_domain_id,
                    project_id=target_project_id,
                    project_name=target_project_name,
                    project_domain_name=target_project_domain_name,
                    project_domain_id=target_project_domain_id)
            else:
                raise RuntimeError("You must either provide a valid token or "
                                   "a password (target_api_key) and a user.")

            target_session = ks_session.Session(auth=target_auth)
            target_auth_headers = target_session.get_auth_headers() or {}

            # NOTE: (sharatss) The target_auth_token is required here so that
            # it can be passed as a separate header later.
            target_auth_token = target_auth_headers.get('X-Auth-Token')

            auth_response.update({
                api.TARGET_AUTH_TOKEN: target_auth_token,
                api.TARGET_PROJECT_ID: target_session.get_project_id(),
                api.TARGET_USER_ID: target_session.get_user_id(),
                api.TARGET_AUTH_URI: target_auth_url,
                api.TARGET_SERVICE_CATALOG: jsonutils.dumps(
                    target_auth.get_access(
                        target_session)._data['access'])
            })

        return auth_response
