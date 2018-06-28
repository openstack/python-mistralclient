========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/badges/python-mistralclient.svg
    :target: https://governance.openstack.org/reference/tags/index.html

Mistral
=======

.. image:: https://img.shields.io/pypi/v/python-mistralclient.svg
    :target: https://pypi.org/project/python-mistralclient/
    :alt: Latest Version

Mistral is a workflow service. Most business processes consist of multiple
distinct interconnected steps that need to be executed in a particular
order in a distributed environment. A user can describe such a process as a set
of tasks and their transitions. After that, it is possible to upload such a
description to Mistral, which will take care of state management, correct
execution order, parallelism, synchronization and high availability.

Mistral also provides flexible task scheduling so that it can run a process
according to a specified schedule (for example, every Sunday at 4.00pm) instead
of running it immediately. In Mistral terminology such a set of tasks and
relations between them is called a workflow.

Mistral client
==============

Python client for Mistral REST API. Includes python library for Mistral API and
Command Line Interface (CLI) library.

Installation
------------

First of all, clone the repo and go to the repo directory::

    $ git clone git://git.openstack.org/openstack/python-mistralclient.git
    $ cd python-mistralclient

Then just run::

    $ pip install -e .

or::

    $ pip install -r requirements.txt
    $ python setup.py install


Running Mistral client
----------------------

If Mistral authentication is enabled, provide the information about OpenStack
auth to environment variables. Type::

    $ export OS_AUTH_URL=http://<Keystone_host>:5000/v2.0
    $ export OS_USERNAME=admin
    $ export OS_TENANT_NAME=tenant
    $ export OS_PASSWORD=secret
    $ export OS_MISTRAL_URL=http://<Mistral host>:8989/v2  (optional, by
      default URL=http://localhost:8989/v2)

and in the case that you are authenticating against keystone over https:

    $ export OS_CACERT=<path_to_ca_cert>

.. note:: In client, we can use both Keystone auth versions - v2.0 and v3. But
          server supports only v3.*

To make sure Mistral client works, type::

    $ mistral workbook-list

You can see the list of available commands typing::

    $ mistral --help

Useful Links
============

* `PyPi`_ - package installation
* `Launchpad project`_ - release management
* `Blueprints`_ - feature specifications
* `Bugs`_ - issue tracking
* `Source`_
* `Specs`_
* `How to Contribute`_

.. _PyPi: https://pypi.org/project/python-mistralclient
.. _Launchpad project: https://launchpad.net/python-mistralclient
.. _Blueprints: https://blueprints.launchpad.net/python-mistralclient
.. _Bugs: https://bugs.launchpad.net/python-mistralclient
.. _Source: https://git.openstack.org/cgit/openstack/python-mistralclient
.. _How to Contribute: https://docs.openstack.org/infra/manual/developers.html
.. _Specs: https://specs.openstack.org/openstack/mistral-specs/
.. _Release Notes: https://docs.openstack.org/releasenotes/python-mistralclient
