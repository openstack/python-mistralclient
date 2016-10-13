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

from mistralclient import auth
from oslo_serialization import jsonutils

import mistralclient.api.httpclient as api


def _get_keystone_client(auth_url):
    if 'v2.0' in auth_url:
        from keystoneclient.v2_0 import client
    else:
        from keystoneclient.v3 import client

    return client


class KeystoneAuthHandler(auth.AuthHandler):

    def authenticate(self, req):
        """Performs authentication via Keystone.

        :param req: Request dict containing list of parameters required
            for Keystone authentication.

        """
        if not isinstance(req, dict):
            raise TypeError('The input "req" is not typeof dict.')

        auth_url = req.get('auth_url')
        mistral_url = req.get('mistral_url')
        endpoint_type = req.get('endpoint_type', 'publicURL')
        service_type = req.get('service_type', 'workflow2')
        username = req.get('username')
        user_id = req.get('user_id')
        api_key = req.get('api_key')
        auth_token = req.get('auth_token')
        project_name = req.get('project_name')
        project_id = req.get('project_id')
        cacert = req.get('cacert')
        region_name = req.get('region_name')
        insecure = req.get('insecure', False)
        target_username = req.get('target_username')
        target_api_key = req.get('target_api_key')
        target_project_name = req.get('target_project_name')
        target_auth_url = req.get('target_auth_url')
        target_project_id = req.get('target_project_id')
        target_auth_token = req.get('target_auth_token')
        target_user_id = req.get('target_user_id')
        target_cacert = req.get('target_cacert')
        target_region_name = req.get('target_region_name')
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

        if auth_url:
            keystone_client = _get_keystone_client(auth_url)

            keystone = keystone_client.Client(
                username=username,
                user_id=user_id,
                password=api_key,
                token=auth_token,
                tenant_id=project_id,
                tenant_name=project_name,
                auth_url=auth_url,
                endpoint=auth_url,
                cacert=cacert,
                insecure=insecure
            )

            keystone.authenticate()

            auth_response.update({
                api.AUTH_TOKEN: keystone.auth_token,
                api.PROJECT_ID: keystone.project_id,
                api.USER_ID: keystone.user_id,
            })

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
            target_keystone_client = _get_keystone_client(target_auth_url)

            target_keystone = target_keystone_client.Client(
                username=target_username,
                user_id=target_user_id,
                password=target_api_key,
                token=target_auth_token,
                tenant_id=target_project_id,
                tenant_name=target_project_name,
                auth_url=target_auth_url,
                endpoint=target_auth_url,
                cacert=target_cacert,
                insecure=target_insecure,
                region_name=target_region_name
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
