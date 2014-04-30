from mistralclient.api import client as mistral_client


def mistralclient(request):
    return mistral_client.Client()
