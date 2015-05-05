Overview
========

Directory Structure
-------------------

The `farmcloud` source code is organized as follows:

.. code-block:: text

    farmcloud/
    +-farmcloud/        # Python module containing farmcloud client
    +-puppet/           # Puppet module for install and config
    | +-scripts/        # Start and stop hooks
    | | +-...
    | +-manifests/
    | | +-site.pp       # Configuration of Puppet install
    | +-...
    +-config/           # Configurations/specifications
    +-zkconf/           # ZooKeeper configuration for local testing

