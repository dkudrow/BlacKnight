Installation
============

This section describes the installation of BlacKnight as well as that of a test environment based on Eucalyptus. A Puppet manifest is provided in the ``puppet/`` directory to make this process marginally less painful. This manifest is not perfect - installation requires some supervision and, in certain cases, multiple passes. To ensure that all necessary components are installed run Puppet repeatedly until no messages are printed. All development was done on CentOS 6.6 (final) and determining whether BlacKnight will run in another environment is left as an exercise for the reader.


Puppet
------

Puppet is a configuration management tool for bootstrapping deployments from a user-specified manifest. Familiarity with puppet is not necessary (you can simply follow the instructions below) but will be helpful for trouble-shooting and required for contributing.

.. admonition:: Install Puppet on all hosts

    #. Run the following commands in a root shell:

    .. code-block:: shell

        $ yum install puppet
        $ puppet module install computology-packagecloud

Configuration of the installation is handled entirely in ``puppet/manifests/site.pp``. Deployment-wide configuration is managed using global variables which are inherited by all hosts. Each host in the deployment is declared in a *node* block. This block contains host-specific information (e.g. hostname, &c.) and several *include* directives. The includes inform puppet of which modules should be applied to the host in question. Any module in ``puppet/modules/`` can be included.

.. code-block:: ruby

    # puppet/manifests/site.pp

    # Global configuration variables
    $CLOUD_OPTS = '--db-home=/usr/pgsql-9.1/ --java-home=/usr/lib/jvm/java-1.7.0'
    ...

    # Node declarations
    node 'oz.cs.ucsb.edu' {

        # Host-specific configuration variables
        $HWADDR = '00:26:B9:3D:16:D2'
        $UUID = '99bb00f0-df2b-437b-9b35-1399c3be2ab2'
        $PUBLIC_IP = '128.111.55.51'
        $IPADDR = '10.50.10.51'
        $HOSTNAME = 'oz.cs.ucsb.edu'

        # Modules to apply on host
        include blacknight
        include riak
        include eucalyptus
    }

    node 'objc.cs.ucsb.edu' {
    ...
.. admonition:: Configure Puppet

    #. Open ``puppet/manifests/site.pp`` in your favorite text editor.

    #. For each physical host you wish to include define a **node** as described above.


BlacKnight
----------

Installing BlacKnight via Puppet is straightforward and requires no manual configuration. BlacKnight itself is distributed as a Python package that can be installed with pip. For convenience, we use the ZooKeeper RPM packaged by Cloudera.

.. admonition:: Installing BlacKnight

    In ``puppet/manifests/site.pp``, add the line

    .. code-block:: ruby

        include blacknight

    to each host's node definition.

    .. code-block:: shell

        # execute the following commands as root.
        cd puppet/
        ./run_puppet


Eucalyptus
----------


RiakCS
^^^^^^


Development
-----------

BlacKnight comes equipped with a series of utilities for simulated execution as testing on a full scale appliance can be unwieldy. The **zkconf** tool is extremely useful for quickly deploying temporary ZooKeeper ensembles; it can be found at FIXME and the instructions are straightforward. The :mod:`util` contains various commands for communicating with a local ZooKeeper server to simulate services. The provided specification (``test/spec.yaml``) simply points hooks at blacknight-util to start and stop simulated services.


External Documentation
----------------------

* Puppet_
* Eucalyptus_
* RiakCS_
* ZooKeeper_
* Kazoo_

.. _Puppet: http://docs.puppetlabs.com/puppet/
.. _Eucalyptus: https://www.eucalyptus.com/docs/eucalyptus/4.1.1/index.html
.. _RiakCS: http://docs.basho.com/riakcs/latest/
.. _ZooKeeper: https://zookeeper.apache.org/doc/r3.5.0-alpha/
.. _Kazoo: https://kazoo.readthedocs.org/en/latest/
