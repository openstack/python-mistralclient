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

import json

from mistralclient.tests import base
from mistralclient.api.listeners import Listener

# TODO: later we need additional tests verifying all the errors etc.

LISTENERS = [
    {
        'id': "1",
        'workbook_name': "my_workbook",
        'description': "My cool Mistral workbook",
        'webhook': "http://my.website.org"
    }
]

URL_TEMPLATE = '/workbooks/%s/listeners'
URL_TEMPLATE_ID = '/workbooks/%s/listeners/%s'


class TestListeners(base.BaseClientTest):
    def test_create(self):
        mock = self.mock_http_post(content=LISTENERS[0])
        body = {
            'workbook_name': LISTENERS[0]['workbook_name'],
            'description': LISTENERS[0]['description'],
            'webhook': LISTENERS[0]['webhook'],
            'events': None
        }

        lsnr = self.listeners.create(LISTENERS[0]['workbook_name'],
                                     LISTENERS[0]['webhook'],
                                     LISTENERS[0]['description'])

        self.assertIsNotNone(lsnr)
        self.assertEqual(Listener(self.listeners, LISTENERS[0]).__dict__,
                         lsnr.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE % (LISTENERS[0]['workbook_name']),
            json.dumps(body))

    def test_update(self):
        mock = self.mock_http_put(content=LISTENERS[0])
        body = {
            'id': LISTENERS[0]['id'],
            'workbook_name': LISTENERS[0]['workbook_name'],
            'description': LISTENERS[0]['description'],
            'webhook': LISTENERS[0]['webhook'],
            'events': None
        }

        lsnr = self.listeners.update(LISTENERS[0]['workbook_name'],
                                     LISTENERS[0]['id'],
                                     LISTENERS[0]['webhook'],
                                     LISTENERS[0]['description'])

        self.assertIsNotNone(lsnr)
        self.assertEqual(Listener(self.listeners, LISTENERS[0]).__dict__,
                         lsnr.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (LISTENERS[0]['workbook_name'],
                               LISTENERS[0]['id']),
            json.dumps(body))

    def test_list(self):
        mock = self.mock_http_get(content={'listeners': LISTENERS})

        listeners = self.listeners.list(LISTENERS[0]['workbook_name'])

        self.assertEqual(1, len(listeners))
        lsnr = listeners[0]

        self.assertEqual(Listener(self.listeners, LISTENERS[0]).__dict__,
                         lsnr.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE % (LISTENERS[0]['workbook_name']))

    def test_get(self):
        mock = self.mock_http_get(content=LISTENERS[0])

        lsnr = self.listeners.get(LISTENERS[0]['workbook_name'],
                                  LISTENERS[0]['id'])

        self.assertEqual(Listener(self.listeners, LISTENERS[0]).__dict__,
                         lsnr.__dict__)
        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (LISTENERS[0]['workbook_name'],
                               LISTENERS[0]['id']))

    def test_delete(self):
        mock = self.mock_http_delete(status_code=204)

        self.listeners.delete(LISTENERS[0]['workbook_name'],
                              LISTENERS[0]['id'])

        mock.assert_called_once_with(
            URL_TEMPLATE_ID % (LISTENERS[0]['workbook_name'],
                               LISTENERS[0]['id']))
