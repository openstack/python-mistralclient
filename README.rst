========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/python-mistralclient.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

Mistral client
==============

Python client for Mistral REST API. Includes python library for Mistral API and Command Line Interface (CLI) library.


Installation
------------

First of all, clone the repo and go to the repo directory:

    | git clone https://git.openstack.org/openstack/python-mistralclient.git
    | cd python-mistralclient

Then just run:

    pip install -e .

or

    | pip install -r requirements.txt
    | python setup.py install


Running Mistral client
----------------------

If Mistral authentication is enabled, provide the information about OpenStack auth to environment variables. Type:

    | export OS_AUTH_URL=http://<Keystone_host>:5000/v2.0
    | export OS_USERNAME=admin
    | export OS_TENANT_NAME=tenant
    | export OS_PASSWORD=secret
    | export OS_MISTRAL_URL=http://<Mistral host>:8989/v2  (optional, by
      default URL=http://localhost:8989/v2)

and in the case that you are authenticating against keystone over https:

    export OS_CACERT=<path_to_ca_cert>

.. note:: In client, we can use both Keystone auth versions - v2.0 and v3. But
          server supports only v3.*

To make sure Mistral client works, type:

    mistral workbook-list

You can see the list of available commands typing:

    mistral --help
