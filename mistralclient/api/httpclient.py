# Copyright 2013 - Mirantis, Inc.
# Copyright 2016 - StackStorm, Inc.
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

import base64
import copy
import os

from oslo_utils import importutils
import requests

import logging


AUTH_TOKEN = 'auth_token'
CACERT = 'cacert'
CERT_FILE = 'cert'
CERT_KEY = 'key'
INSECURE = 'insecure'
PROJECT_ID = 'project_id'
TARGET_AUTH_TOKEN = 'target_auth_token'
TARGET_AUTH_URI = 'target_auth_url'
TARGET_PROJECT_ID = 'target_project_id'
TARGET_USER_ID = 'target_user_id'
TARGET_SERVICE_CATALOG = 'target_service_catalog'
USER_ID = 'user_id'

osprofiler_web = importutils.try_import("osprofiler.web")

LOG = logging.getLogger(__name__)


def log_request(func):
    def decorator(self, *args, **kwargs):
        resp = func(self, *args, **kwargs)
        LOG.debug("HTTP %s %s %d" % (resp.request.method, resp.url,
                  resp.status_code))
        return resp
    return decorator


class HTTPClient(object):
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.auth_token = kwargs.get(AUTH_TOKEN)
        self.project_id = kwargs.get(PROJECT_ID)
        self.user_id = kwargs.get(USER_ID)
        self.target_auth_token = kwargs.get(TARGET_AUTH_TOKEN)
        self.target_auth_uri = kwargs.get(TARGET_AUTH_URI)
        self.target_user_id = kwargs.get(TARGET_USER_ID)
        self.target_project_id = kwargs.get(TARGET_PROJECT_ID)
        self.target_service_catalog = kwargs.get(TARGET_SERVICE_CATALOG)
        self.cacert = kwargs.get(CACERT)
        self.insecure = kwargs.get(INSECURE, False)
        self.ssl_options = {}

        if self.base_url.startswith('https'):
            if self.cacert and not os.path.exists(self.cacert):
                raise ValueError('Unable to locate cacert file '
                                 'at %s.' % self.cacert)

            if self.cacert and self.insecure:
                LOG.warning('Client is set to not verify even though '
                            'cacert is provided.')

            if self.insecure:
                self.ssl_options['verify'] = False
            else:
                if self.cacert:
                    self.ssl_options['verify'] = self.cacert
                else:
                    self.ssl_options['verify'] = True

            self.ssl_options['cert'] = (
                kwargs.get(CERT_FILE),
                kwargs.get(CERT_KEY)
            )

    @log_request
    def get(self, url, headers=None):
        options = self._get_request_options('get', headers)

        return requests.get(self.base_url + url, **options)

    @log_request
    def post(self, url, body, headers=None):
        options = self._get_request_options('post', headers)

        return requests.post(self.base_url + url, body, **options)

    @log_request
    def put(self, url, body, headers=None):
        options = self._get_request_options('put', headers)

        return requests.put(self.base_url + url, body, **options)

    @log_request
    def delete(self, url, headers=None):
        options = self._get_request_options('delete', headers)

        return requests.delete(self.base_url + url, **options)

    def _get_request_options(self, method, headers):
        headers = self._update_headers(headers)

        if method in ['post', 'put']:
            content_type = headers.get('content-type', 'application/json')
            headers['content-type'] = content_type

        options = copy.deepcopy(self.ssl_options)
        options['headers'] = headers

        return options

    def _update_headers(self, headers):
        if not headers:
            headers = {}

        if self.auth_token:
            headers['x-auth-token'] = self.auth_token

        if self.project_id:
            headers['X-Project-Id'] = self.project_id

        if self.user_id:
            headers['X-User-Id'] = self.user_id

        if self.target_auth_token:
            headers['X-Target-Auth-Token'] = self.target_auth_token

        if self.target_auth_uri:
            headers['X-Target-Auth-Uri'] = self.target_auth_uri

        if self.target_project_id:
            headers['X-Target-Project-Id'] = self.target_project_id

        if self.target_user_id:
            headers['X-Target-User-Id'] = self.target_user_id

        if self.target_service_catalog:
            headers['X-Target-Service-Catalog'] = base64.b64encode(
                self.target_service_catalog.encode('utf-8')
            )

        if osprofiler_web:
            # Add headers for osprofiler.
            headers.update(osprofiler_web.get_trace_id_headers())

        return headers
