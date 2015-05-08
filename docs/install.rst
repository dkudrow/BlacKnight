.. role:: shell(code)
    :language: shell

Installation
============

All of the components of farmcloud can be installed using the Puppet module
in the :shell:`puppet/` directory. The Puppet module is not perfect - it
requires supervision and, in some cases, multiple passes. To ensure that all
necessary components are installed run puppet repeatedly until no messages
are printed. All development was done on CentOS 6.6 (final) and determining
whether it runs in another environment is left as an exercise for the
reader.

Overview
--------
Farmcloud requires of the following components and their dependencies to be
installed on all nodes:

    - Eucalyptus_
    - RiakCS_
    - ZooKeeper_
    - Kazoo_

.. _Eucalyptus: https://www.eucalyptus.com/docs/eucalyptus/4.1.0/index.html
.. _RiakCS: http://docs.basho.com/riakcs/latest/
.. _ZooKeeper: https://zookeeper.apache.org/doc/r3.5.0-alpha/
.. _Kazoo: https://kazoo.readthedocs.org/en/latest/

Puppet
------

- Install Puppet

.. code-block:: shell

    yum install Puppet

- In order to install Riak we need Puppet's PackageCloud module

.. code-block:: shell

    puppet module install computology-packagecloud

The puppet installation is configured via global variables in
:shell:`puppet/manifests/site.pp`. Most of these variables mirror the
configuration variables of the various components of FarmCloud (i.e. those
found in :code:`eucalyptus.conf`, :code:`riak.conf`, &c.) Below  are described
the few of these that **must** be changed in order to run FarmCloud.  For
information about the rest, consult the documentation of the corresponding
components. To add a variable, simply define it in
:code:`puppet/manifests/site.pp` and add it to corresponding config file in
:code:`puppet/modules/<module>/templates/<config_file>.erb`

Eucalyptus
----------
Below are the configuration variables that **must** set in order for
Eucalyptus to run. All of the variables mirror keys in eucalyptus.conf. To
add a variable, simply define it in :code:`site.pp` and add it to
:code:`puppet/modules/config/tempaltes/eucalyptus.conf.erb`.

    - :code:`VNET_SUBNET` - subnet on which Eucalyptus nodes run
    - :code:`VNET_NETMASK` - subnet mask for the Eucalyptus bridge network
    - :code:`VNET_DNS` - IP address of DNS server

Riak CS
-------

- Riak CS

    - `RIAKCS_PORT` - the deafult Riak CS port (8080) conflicts with Eucalyptus so this must be changed
    - `STANCHION_HOST` - one node in the Riak CS deployment must also run Stanchion

ZooKeeper
---------

Notes
-----
- must distribute keys across all machines (for Eucalyptus)
- must start each component manually on each machine?
- for some reason can't run euca_conf --get-credentials on secondary