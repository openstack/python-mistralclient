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

from keystoneclient import client
from mistralclient import auth
from oslo_serialization import jsonutils

import mistralclient.api.httpclient as api


class KeystoneAuthHandler(auth.AuthHandler):

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
        user_domain_name = req.get('user_domain_name', 'Default')
        project_domain_name = req.get('project_domain_name', 'Default')
        cacert = req.get('cacert')
        insecure = req.get('insecure', False)

        target_auth_url = req.get('target_auth_url')
        target_username = req.get('target_username')
        target_user_id = req.get('target_user_id')
        target_api_key = req.get('target_api_key')
        target_auth_token = req.get('target_auth_token')
        target_project_name = req.get('target_project_name')
        target_project_id = req.get('target_project_id')
        target_region_name = req.get('target_region_name')
        target_user_domain_name = req.get('target_user_domain_name', 'Default')
        target_project_domain_name = req.get(
            'target_project_domain_name',
            'Default'
        )
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

        if session:
            keystone = client.Client(session=session)
        elif auth_url:
            keystone = client.Client(
                username=username,
                user_id=user_id,
                password=api_key,
                token=auth_token,
                tenant_id=project_id,
                tenant_name=project_name,
                auth_url=auth_url,
                cacert=cacert,
                insecure=insecure,
                user_domain_name=user_domain_name,
                project_domain_name=project_domain_name
            )
            keystone.authenticate()
            auth_response.update({
                api.AUTH_TOKEN: keystone.auth_token,
                api.PROJECT_ID: keystone.project_id,
                api.USER_ID: keystone.user_id,
            })

        if session or auth_url:
            if not mistral_url:
                try:
                    mistral_url = keystone.service_catalog.url_for(
                        service_type=service_type,
                        endpoint_type=endpoint_type,
                        region_name=region_name
                    )
                except Exception:
                    mistral_url = None

            auth_response['mistral_url'] = mistral_url

        if target_auth_url:
            target_keystone = client.Client(
                username=target_username,
                user_id=target_user_id,
                password=target_api_key,
                token=target_auth_token,
                tenant_id=target_project_id,
                tenant_name=target_project_name,
                project_id=target_project_id,
                project_name=target_project_name,
                auth_url=target_auth_url,
                cacert=target_cacert,
                insecure=target_insecure,
                region_name=target_region_name,
                user_domain_name=target_user_domain_name,
                project_domain_name=target_project_domain_name
            )

            target_keystone.authenticate()

            auth_response.update({
                api.TARGET_AUTH_TOKEN: target_keystone.auth_token,
                api.TARGET_PROJECT_ID: target_keystone.project_id,
                api.TARGET_USER_ID: target_keystone.user_id,
                api.TARGET_AUTH_URI: target_auth_url,
                api.TARGET_SERVICE_CATALOG: jsonutils.dumps(
                    target_keystone.auth_ref
                )
            })

        return auth_response
