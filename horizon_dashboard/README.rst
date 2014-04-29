====================================
Horizon Customization Demo Dashboard
====================================

This Django project demonstrates how the `Horizon`_ app can be used to
construct customized dashboards (for OpenStack or anything else).

The ``horizon`` module is pulled down from GitHub during setup
(see setup instructions below) and added to the virtual environment.

.. _Horizon: http://github.com/openstack/horizon

Setup Instructions
==================

The following should get you started::

    $ git clone https://github.com/stackforge/python-mistralclient.git
    $ cd python-mistralclient/horizon_dashboard
    $ cp demo_dashboard/local/local_settings.py.example \
      demo_dashboard/local/local_settings.py

Edit the ``local_settings.py`` file as needed. Make sure you have changed
OPENSTACK_HOST to point to your keystone server and also check all endpoints
are accessible. You may want to change OPENSTACK_ENDPOINT_TYPE to "publicURL"
if some of your endpoints are inaccessible.

You may also need to add a service and endpoints to keystone::

    $ MISTRAL_URL="http://[host]:[port]/v1"
    $ keystone service-create --name mistral --type workflow
    $ keystone endpoint-create --service_id mistral --publicurl $MISTRAL_URL \
      --adminurl $MISTRAL_URL --internalurl $MISTRAL_URL

When you're ready to run the development server::

    $ ./run_tests.sh --runserver


