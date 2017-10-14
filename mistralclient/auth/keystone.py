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

import keystoneauth1.access.service_catalog as sc
import keystoneauth1.identity.generic as auth_plugin
from keystoneauth1 import session as ks_session
import mistralclient.api.httpclient as api
from mistralclient import auth as mistral_auth
from oslo_serialization import jsonutils


LOG = logging.getLogger(__name__)


class KeystoneAuthHandler(mistral_auth.AuthHandler):

    def authenticate(self, req, session=None):
        """Perform authentication via Keystone.

        :param req: Request dict containing the parameters required
            for Keystone authentication.
        """
        reqs = self._separate_target_reqs(req)
        try:
            result = self._authenticate(reqs, session)
        except Exception as e:
            if "Cannot use v2 authentication with domain scope" in str(e):
                LOG.warning("Client tried to use v2 authentication with "
                            "domain scope. Domain parameters are assumed "
                            "to be erroneously set. Retrying "
                            "authentication without them. "
                            "Request parameters: %s" % str(reqs))
                domainless_reqs = [reqs[0],
                                   self._remove_domain(reqs[1])]
                result = self._authenticate(domainless_reqs, session)
            else:
                raise
        return result

    @staticmethod
    def _separate_target_reqs(req):
        """Separates parameters into target and non-target ones.

        target_* parameters are rekeyed by removing the prefix.

        :param req: Request dict containing the parameters for Keystone
        authentication.
        :return: list of [non-target, target] request parameters
        """
        r = {}
        target_r = {}
        target_prefix = "target_"
        for key in req:
            if key.startswith(target_prefix):
                target_r[key[len(target_prefix):]] = req[key]
            else:
                r[key] = req[key]

        return [r, target_r]

    @staticmethod
    def _remove_domain(req):
        """Remove all domain parameters from req.

        Keystoneauth with V2 does not accept domain parameters. This
        is an incompatible change from Keystoneclient but it would
        unnecessarily break clients of Mistral. It is safe to remove
        domain parameters if V2 auth is targeted.

        :param req: Request dict containing list of parameters required
        :return: Request dict without domains
        """
        r = {}
        for key in req:
            if "domain" not in key:
                r[key] = req[key]
        return r

    @staticmethod
    def _get_auth(api_key=None, auth_token=None, auth_url=None,
                  project_domain_id=None, project_domain_name=None,
                  project_id=None, project_name=None, user_domain_id=None,
                  user_domain_name=None, user_id=None, username=None,
                  **kwargs):

        if project_name and project_id:
            raise RuntimeError(
                'Only one of project_name or project_id should be set'
            )

        if username and user_id:
            raise RuntimeError(
                'Only one of username or user_id should be set'
            )

        auth = {}

        if auth_token:
            auth = auth_plugin.Token(
                auth_url=auth_url,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name,
                project_id=project_id,
                project_name=project_name,
                token=auth_token
            )
        elif api_key and (username or user_id):
            auth = auth_plugin.Password(
                auth_url=auth_url,
                password=api_key,
                project_domain_id=project_domain_id,
                project_domain_name=project_domain_name,
                project_id=project_id,
                project_name=project_name,
                user_domain_id=user_domain_id,
                user_domain_name=user_domain_name,
                user_id=user_id,
                username=username
            )

        return auth

    def _authenticate(self, reqs, session=None):
        """Performs authentication via Keystone.

        :param reqs: Request dict containing list of parameters required
            for Keystone authentication.
        :return: Auth response dict
        """
        if not isinstance(reqs[0], dict):
            raise TypeError('The input "req" is not typeof dict.')
        if not isinstance(reqs[1], dict):
            raise TypeError('The input "req" is not typeof dict.')

        auth_response = {}
        req = reqs[0]
        cacert = req.get('cacert')
        endpoint_type = req.get('endpoint_type', 'publicURL')
        insecure = req.get('insecure')
        mistral_url = req.get('mistral_url')
        region_name = req.get('region_name')
        service_type = req.get('service_type', 'workflowv2')

        verify = self._verification_needed(cacert, insecure)

        if not session:
            auth = self._get_auth(**req)

            if auth:
                session = ks_session.Session(auth=auth, verify=verify)

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

        target_req = reqs[1]

        if "auth_url" in target_req:
            target_auth = self._get_auth(**target_req)

            if target_auth:

                # target cacert and insecure
                cacert = target_req.get('cacert')
                insecure = target_req.get('insecure')

                verify = self._verification_needed(cacert, insecure)

                target_session = ks_session.Session(
                    auth=target_auth,
                    verify=verify
                )

                target_auth_headers = target_session.get_auth_headers() or {}

                target_auth_token = target_auth_headers.get('X-Auth-Token')

                auth_response.update({
                    api.TARGET_AUTH_TOKEN: target_auth_token,
                    api.TARGET_PROJECT_ID: target_session.get_project_id(),
                    api.TARGET_USER_ID: target_session.get_user_id(),
                    api.TARGET_AUTH_URI: target_auth._plugin.auth_url,
                })

                access = target_auth.get_access(target_session)
                service_catalog = access.service_catalog

                if self._is_service_catalog_v2(service_catalog):
                    access_data = access._data["access"]
                    if not len(access_data['serviceCatalog']):
                        LOG.warning(
                            "Service Catalog empty, some authentication"
                            "credentials may be missing. This can cause"
                            "malfunction in the Mistral action executions.")
                    sc_json = jsonutils.dumps(access_data)
                    auth_response[api.TARGET_SERVICE_CATALOG] = sc_json

        if not auth_response:
            LOG.debug("No valid token or password + user provided. "
                      "Continuing without authentication")
            return {}

        return auth_response

    @staticmethod
    def _verification_needed(cacert, insecure):
        """Return the verify parameter.

        The value of verify can be either True/False or a cacert.

        :param cacert None or path to CA cert file
        :param insecure truthy value to switch on SSL verification
        """
        if insecure is False or insecure is None:
            verify = cacert or True
        else:
            verify = False
        return verify

    @staticmethod
    def _is_service_catalog_v2(catalog):
        """Check if the service catalog is of type ServiceCatalogV2

        :param catalog: the service catalog
        :return: True if V2, False otherwise
        """
        return type(catalog) is sc.ServiceCatalogV2
