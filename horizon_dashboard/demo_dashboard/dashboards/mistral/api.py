from django.conf import settings

from mistralclient.api import client as mistral_client

SERVICE_TYPE = 'workflow'


def mistralclient(request):
    return mistral_client.Client(
        username=request.user.username,
        auth_token=request.user.token.id,
        project_id=request.user.tenant_id,
        # Ideally, we should get it from identity endpoint, but since
        # python-mistralclient is not supporting v2.0 API it might create
        # additional troubles for those who still rely on v2.0 stack-wise.
        auth_url=getattr(settings, 'OPENSTACK_KEYSTONE_URL'),
        # Todo: add SECONDARY_ENDPOINT_TYPE support
        endpoint_type=getattr(settings,
                              'OPENSTACK_ENDPOINT_TYPE',
                              'internalURL'),
        service_type=SERVICE_TYPE)
