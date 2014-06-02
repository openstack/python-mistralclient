# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
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

import requests

import logging


LOG = logging.getLogger(__name__)


def log_request(func):
    def decorator(self, *args, **kwargs):
        resp = func(self, *args, **kwargs)
        LOG.debug("HTTP %s %s %d" % (resp.request.method, resp.url,
                  resp.status_code))
        return resp
    return decorator


class HTTPClient(object):
    def __init__(self, base_url, token=None, project_id=None, user_id=None):
        self.base_url = base_url
        self.token = token
        self.project_id = project_id
        self.user_id = user_id

    @log_request
    def get(self, url, headers=None):
        headers = self._update_headers(headers)

        return requests.get(self.base_url + url, headers=headers)

    @log_request
    def post(self, url, body, headers=None):
        headers = self._update_headers(headers)
        content_type = headers.get('content-type', 'application/json')
        headers['content-type'] = content_type

        return requests.post(self.base_url + url, body, headers=headers)

    @log_request
    def put(self, url, body, headers=None):
        headers = self._update_headers(headers)
        content_type = headers.get('content-type', 'application/json')
        headers['content-type'] = content_type

        return requests.put(self.base_url + url, body, headers=headers)

    @log_request
    def delete(self, url, headers=None):
        headers = self._update_headers(headers)

        return requests.delete(self.base_url + url, headers=headers)

    def _update_headers(self, headers):
        if not headers:
            headers = {}

        token = headers.get('x-auth-token', self.token)
        if token:
            headers['x-auth-token'] = token

        project_id = headers.get('X-Project-Id', self.project_id)
        if project_id:
            headers['X-Project-Id'] = project_id

        user_id = headers.get('X-User-Id', self.user_id)
        if user_id:
            headers['X-User-Id'] = user_id

        return headers
