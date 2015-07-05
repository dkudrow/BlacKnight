Installation
============

This section describes the installation of BlacKnight as well as that of a test environment based on Eucalyptus. A Puppet manifest is provided in the ``puppet/`` directory to make this process marginally less painful. This manifest is not perfect - installation requires some supervision and, in certain cases, multiple passes. To ensure that all necessary components are installed run Puppet repeatedly until no messages are printed. All development was done on CentOS 6.6 (final) and determining whether BlacKnight will run in another environment is left as an exercise for the reader.

.. tip::

    The installation steps will be contained inside of *tip* boxes like this one. To get through the installation with minimal reading, just jump from one tip box to the next.


Puppet
------

Puppet is a configuration management tool for bootstrapping deployments from a user-specified manifest. Familiarity with puppet is not necessary (you can simply follow the instructions below) but will be helpful for trouble-shooting and required for contributing. It must be present on all hosts in order to be used for the installation.

.. tip::

    Run the following commands as root on each host to install Puppet:

    .. code-block:: shell

        yum install puppet
        puppet module install computology-packagecloud
        puppet module install stankevich-python


Configuration of the installation is handled entirely within ``puppet/manifests/site.pp``. Deployment-wide configuration is managed using global variables which are inherited by all hosts. Each host in the deployment is declared in a *node* block. This block contains host-specific information (e.g. hostname, &c.) and several *include* directives. The includes inform puppet of which modules should be applied to the host in question. Any module in ``puppet/modules/`` can be included.

.. tip::

    Open ``puppet/manifests/site.pp`` and using the template below as a guide

        1. define a *node* for each host in the appliance using the template below as a guide.

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


BlacKnight
----------

Installing BlacKnight via Puppet is straightforward and requires no manual configuration. BlacKnight itself is distributed as a Python package that can be installed with pip. For convenience, we use the ZooKeeper RPM packaged by Cloudera.

.. tip::

    In ``site.pp``, add the line

    .. code-block:: ruby

        include blacknight

    to each node on which BlacKnight should be installed. Apply the manifest by running the following commands as root.

    .. code-block:: shell

        # execute the following commands as root.
        cd puppet/
        ./run_puppet


RiakCS
------

.. warning::

    In the following line of ``/etc/riak/advanced.config``,

    .. code-block:: erlang

          {add_paths, ["/usr/lib64/riak-cs/lib/riak_cs-2.0.1/ebin"]},

    the version string (*2.0.1* above) must match the installed verson of RiakCS or Riak will not start!


Starting
^^^^^^^^

.. code-block:: shell

    # execute the following commands as root on the first host
    riak start
    stanchion start
    riak-cs start

.. code-block:: shell

    # execute the following commands as root on the remaining hosts
    riak start
    riak-cs start
    riak-admin cluster join <nodename_of_first_node>
    riak-admin plan
    riak-admin comit


Eucalyptus
----------


Starting
^^^^^^^^

1. Start primary head components

.. code-block:: shell

    # execute the following commands as root on first host
    rm -rf /var/lib/eucalyptus/db/
    euca_conf --initialize
    service eucalyptus-cloud start
    # wait until CLC is up (check /var/log/eucalyptus/cloud-output.log)
    service eucalyptus-cc start

2. Start secondary head components

.. code-block:: shell

    # execute the following command as root on second host
    rm -rf /var/lib/eucalyptus/db/
    service eucalyptus-cloud start
    # wait until CLC is up (check /var/log/eucalyptus/cloud-output.log)
    service eucalyptus-cc start

3. Register the secondary head

.. code-block:: shell

    # execute the following commands as root on first host
    # <public_ip> and <hostname> refer to the secondary head
    euca_conf --register-cloud -P eucalyptus -H <public_ip> -C <hostname>-clc

4. Register the Eucalyptus APIs

.. code-block:: shell

    # on both the primary and the secondary
    euca_conf --register-service -T user-api -H <public_ip> -N <host>-api


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
