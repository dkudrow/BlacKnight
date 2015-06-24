Installation
============

This section walks through the installation of BlacKnight as well as that of a test environment based on Eucalyptus. A Puppet module is provided in the ``puppet/`` directory to make this process marginally less painful. The module is not perfect - it requires some supervision and, in some cases, multiple passes. To ensure that all necessary components are installed run puppet repeatedly until no messages are printed. All development was done on CentOS 6.6 (final) and determining whether it runs in another environment is left as an exercise for the reader.


Puppet
------

Install Puppet
::

    yum install puppet


Install the PackageCloud Puppet module (needed for Riak)
::

    puppet module install computology-packagecloud

BlacKnight
----------


Eucalyptus
----------


Overview
--------

BlacKnight requires of the following components and their dependencies to be
installed on all nodes:

    - Eucalyptus_
    - RiakCS_
    - ZooKeeper_
    - Kazoo_

.. _Eucalyptus: https://www.eucalyptus.com/docs/eucalyptus/4.1.0/index.html
.. _RiakCS: http://docs.basho.com/riakcs/latest/
.. _ZooKeeper: https://zookeeper.apache.org/doc/r3.5.0-alpha/
.. _Kazoo: https://kazoo.readthedocs.org/en/latest/
