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

import copy
import os

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
    def __init__(self, base_url, token=None, project_id=None, user_id=None,
                 cacert=None, insecure=False):
        self.base_url = base_url
        self.token = token
        self.project_id = project_id
        self.user_id = user_id
        self.ssl_options = {}

        if self.base_url.startswith('https'):
            if cacert and not os.path.exists(cacert):
                raise ValueError('Unable to locate cacert file '
                                 'at %s.' % cacert)

            if cacert and insecure:
                LOG.warning('Client is set to not verify even though '
                            'cacert is provided.')

            self.ssl_options['verify'] = not insecure
            self.ssl_options['cert'] = cacert

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
