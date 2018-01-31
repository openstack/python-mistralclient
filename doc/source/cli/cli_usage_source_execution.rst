Replicating Workflows with Mistral
==================================

The new command line switch '-s' will allow the operator to replicate / clone
an existing workflow execution based on its ID. Once id is given mistral will
create a new workflow execution based on the parameters of the first, which
will provide a simple approach to spawning a number of workflow executions
without having to specify inputs or parameters. Otherwise you can override
some of the parameters (e.g. some of the input variables)

Basic Usage
-----------

From the command line the operator will issue the following. The first step
would be to list the current executions, which is done with "execution-list".
The following step is to take the listed execution id and pass it to the source
execution switch "-s".

.. code-block:: shell

    mistral execution-list

    mistral execution-create -s <execution id>

Once the workflow execution is selected and the replicate command used you
should see a newly created workflow execution based on an existing one with
a new execution id.

.. code-block:: shell

    mistral execution-create -s 123e4567-e89b-12d3-a456-426655440000

+--------------------+---------------------------------------+
| Field              | Value                                 |
+--------------------+---------------------------------------+
| ID                 | 123e4567-e89b-12d3-a456-77046883182e  |
|                    |                                       |
| Workflow ID        | 123e4567-e89b-12d3-a456-45411dfa33af  |
|                    |                                       |
| Workflow name      | some.workflow.name.goes.here          |
|                    |                                       |
| Workflow namespace |                                       |
|                    |                                       |
| Description        |                                       |
|                    |                                       |
| Task Execution ID  | <none>                                |
|                    |                                       |
| State              | RUNNING                               |
|                    |                                       |
| State info         | None                                  |
|                    |                                       |
| Created at         | 2018-01-25 18:41:07                   |
|                    |                                       |
| Updated at         | 2018-01-25 18:41:07                   |
+--------------------+---------------------------------------+
