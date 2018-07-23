Python bindings to the OpenStack Workflow API
=============================================

This is a client for OpenStack Mistral API. There's a Python API
(the :mod:`mistralclient` module), and a command-line script
(installed as :program:`mistral`).

Using mistralclient
-------------------

.. toctree::
   :maxdepth: 2

   cli/cli_usage_with_openstack
   cli/cli_usage_with_keycloak
   cli/cli_usage_targeting_workflows
   cli/cli_usage_source_execution
   class_reference

For information about using the mistral command-line client, see
`Workflow service command-line client`_.

.. _Workflow service command-line client: https://docs.openstack.org/mistral/latest/cli/index.html

Python API Reference
--------------------

* `REST API Specification`_

.. _REST API Specification: https://docs.openstack.org/mistral/latest/api/v2.html

Contributing
------------

Code is hosted `on GitHub`_. Submit bugs to the python-mistralclient project on
`Launchpad`_. Submit code to the openstack/python-mistralclient project
using `Gerrit`_.

.. _on GitHub: https://github.com/openstack/python-mistralclient
.. _Launchpad: https://launchpad.net/python-mistralclient
.. _Gerrit: https://docs.openstack.org/infra/manual/developers.html#development-workflow
