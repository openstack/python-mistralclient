Using Mistral to execute Workflows on an arbitrary cloud
========================================================

It is possible to execute a workflow on any arbitrary cloud without additional
configuration on the Mistral server side. It is possible to have Mistral use
an external OpenStack cloud even when it isn't deployed in an OpenStack
environment (i.e. no Keystone integration).

This setup is particularly useful when Mistral is used in standalone mode,
where the Mistral service is not part of the OpenStack cloud and runs
separately.

To enable this operation, the user can use ``--os-target-username``,
``--os-target-password``, ``--os-target-tenant-id``,
``--os-target-tenant-name``, ``--os-target-auth-token``,
``--os-target-auth-url``, ``--os-target_cacert``, and
``--os-target-region-name`` parameters.

For example, the user can return the heat stack list with this setup as shown
below:

.. code-block:: shell

    $ mistral \
        --os-target-auth-url=http://keystone2.example.com:5000/v3 \
        --os-target-username=testuser \
        --os-target-tenant=testtenant \
        --os-target-password="MistralRuleZ" \
        --os-mistral-url=http://mistral.example.com:8989/v2 \
        run-action heat.stacks_list

The OS-TARGET-* parameters can be set in environment variables as:

.. code-block:: shell

    $ export OS_TARGET_AUTH_URL=http://keystone2.example.com:5000/v3
    $ export OS_TARGET_USERNAME=admin
    $ export OS_TARGET_TENANT_NAME=tenant
    $ export OS_TARGET_PASSWORD=secret
    $ export OS_TARGET_REGION_NAME=region

Note on the --os-target_cacert parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `--os-target_cacert` parameter can be used to set a CA certificate for
SSL communication with the target cloud's Keystone service. The CA certificate
file is **NOT** transferred to the Mistral server. It is the responsibility of
the user to ensure that the SSL Certificate is accessible for the Mistral
Executor and SSL communication is possible with the target cloud. For testing
purposes it is suggested to use the `--target_insecure` parameter.
