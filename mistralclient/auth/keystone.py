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


def authenticate(mistral_url=None, username=None,
                 api_key=None, project_name=None, auth_url=None,
                 project_id=None, endpoint_type='publicURL',
                 service_type='workflowv2', auth_token=None, user_id=None,
                 cacert=None, insecure=False):

    if project_name and project_id:
        raise RuntimeError(
            'Only project name or project id should be set'
        )

    if username and user_id:
        raise RuntimeError(
            'Only user name or user id should be set'
        )

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

    token = keystone.auth_token
    user_id = keystone.user_id
    project_id = keystone.project_id

    if not mistral_url:
        catalog = keystone.service_catalog.get_endpoints(
            service_type=service_type,
            endpoint_type=endpoint_type
        )

        if service_type in catalog:
            service = catalog.get(service_type)
            mistral_url = service[0].get(
                endpoint_type) if service else None

    return mistral_url, token, project_id, user_id


def _get_keystone_client(auth_url):
    if "v2.0" in auth_url:
        from keystoneclient.v2_0 import client
    else:
        from keystoneclient.v3 import client

    return client
