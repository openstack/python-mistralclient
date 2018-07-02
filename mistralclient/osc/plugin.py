#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""OpenStackClient plugin for Workflow service."""

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_WORKFLOW_API_VERSION = '2'
API_VERSION_OPTION = 'os_workflow_api_version'
API_NAME = 'workflow_engine'
API_VERSIONS = {
    '2': 'mistralclient.api.v2.client.Client',
}


def make_client(instance):
    """Returns a workflow_engine service client."""
    version = instance._api_version[API_NAME]
    workflow_client = utils.get_client_class(
        API_NAME,
        version,
        API_VERSIONS)

    LOG.debug('Instantiating workflow engine client: %s', workflow_client)

    mistral_url = instance.get_endpoint_for_service_type(
        'workflowv2',
        region_name=instance.region_name,
        interface='publicURL'
    )

    client = workflow_client(mistral_url=mistral_url, session=instance.session)

    return client


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-workflow-api-version',
        metavar='<workflow-api-version>',
        default=utils.env(
            'OS_WORKFLOW_API_VERSION',
            default=DEFAULT_WORKFLOW_API_VERSION),
        help='Workflow API version, default=' +
             DEFAULT_WORKFLOW_API_VERSION +
             ' (Env: OS_WORKFLOW_API_VERSION)')

    return parser
