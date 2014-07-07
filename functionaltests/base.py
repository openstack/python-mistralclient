import os
import testtools

from tempest import clients
from tempest.common import rest_client

from mistralclient.api import client as mclient


class ClientAuth(rest_client.RestClient):
    def __init__(self, auth_provider):
        super(ClientAuth, self).__init__(auth_provider)

        self.mistral_client = mclient.Client(
            auth_token=self.auth_provider.get_token())


class MistralBase(testtools.TestCase):

    @classmethod
    def setUpClass(cls):
        super(MistralBase, cls).setUpClass()

        mgr = clients.Manager()
        cls.mistral_client = ClientAuth(mgr.auth_provider).mistral_client

        __location = os.path.realpath(os.path.join(os.getcwd(),
                                                   os.path.dirname(__file__)))

        cls.definition = open(os.path.join(
            __location, 'hello.yaml'), 'rb').read()

        cls.wb = cls.mistral_client_workbooks.create(
            "wb", "Description", ["tags"])

    @classmethod
    def tearDownClass(cls):
        super(MistralBase, cls).tearDownClass()

        for wb in cls.mistral_client.workbooks.list():
            cls.mistral_client.workbooks.delete(wb.name)

    def assert_item_in_list(self, items, **props):
        def _matches(item, **props):
            for prop_name, prop_val in props.iteritems():
                v = item[prop_name] if isinstance(item, dict) \
                    else getattr(item, prop_name)

                if v != prop_val:
                    return False

            return True

        filtered_items = filter(lambda item: _matches(item, **props), items)

        return len(filtered_items) != 0
