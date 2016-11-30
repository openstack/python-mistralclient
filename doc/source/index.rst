Python bindings to the OpenStack Workflow API
=============================================

This is a client for OpenStack Mistral API. There's a Python API
(the :mod:`mistralclient` module), and a command-line script
(installed as :program:`mistral`).

Using mistralclient
-------------------

.. toctree::
   :maxdepth: 1

   cli_usage_with_openstack
   cli_usage_with_keycloak
   cli_usage_without_auth

For information about using the mistral command-line client, see
`Workflow service command-line client`_.

.. _Workflow service command-line client: http://docs.openstack.org/cli-reference/mistral.html

Python API Reference
--------------------

* `REST API Specification`_

.. _REST API Specification: http://docs.openstack.org/developer/mistral/developer/webapi/v2.html

Contributing
------------

Code is hosted `on GitHub`_. Submit bugs to the python-mistralclient project on
`Launchpad`_. Submit code to the openstack/python-heatclient project
using `Gerrit`_.

.. _on GitHub: https://github.com/openstack/python-mistralclient
.. _Launchpad: https://launchpad.net/python-mistralclient
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow
