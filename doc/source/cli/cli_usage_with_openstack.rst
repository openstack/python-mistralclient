Using Mistral with OpenStack
============================

The **mistral** shell utility interacts with OpenStack Mistral API from the
command-line. It supports the features in the OpenStack Mistral API.

Basic Usage
-----------

In order to use the CLI, you must provide your OpenStack credentials
(for both user and project), and auth endpoint. Use the corresponding
configuration options (``--os-username``, ``--os-password``,
``--os-project-name``, ``--os-user-domain-id``, ``os-project-domain-id``, and
``--os-auth-url``), but it is easier to set them in environment variables.

.. code-block:: shell

    $ export OS_AUTH_URL=http://<Keystone_host>:5000/v2.0
    $ export OS_USERNAME=admin
    $ export OS_TENANT_NAME=tenant
    $ export OS_PASSWORD=secret
    $ export OS_MISTRAL_URL=http://<Mistral host>:8989/v2

When authenticating against keystone over https:

.. code-block:: shell

    $ export OS_CACERT=<path_to_ca_cert>

Once you've configured your authentication parameters, you can run **mistral**
commands.  All commands take the form of::

    mistral <command> [arguments...]

Run **mistral --help** to get a full list of all possible commands, and run
**mistral help <command>** to get detailed help for that command.
