Installation
============

All of the components of farmcloud can be installed using the Puppet module
in the `puppet/` directory. The Puppet module is not perfect - it requires
supervision and, in some cases, multiple passes. To ensure that all
necessary components are installed run puppet repeatedly until no messages
are printed. All development was done on CentOS 6.6 (final) and determining
whether it runs in another environment is left as an exercise for the
reader.

Puppet
------

1. Install Puppet

.. code-block:: shell

    yum install Puppet

#. In order to install Riak we need Puppet's PackageCloud module

.. code-block:: shell

    puppet module install computology-packagecloud

#. The installation is configured via global variables in
   `puppet/manifests/site.pp`. Most of these can be left as is however the
   following variables need to be modified.

Eucalyptus
----------
*Most of these variables mirror keys in eucalyptus.conf. Consult the Eucalyptus documentation for more information about each.*

        - `NETWORK` - subnet on which Eucalyptus nodes run; this is used to configure the bridge interfaces
        - `NETMASK` - subnet mask for the Eucalyptus bridge network
        - `VNET_PUBLICIPS` - public IP addresses available to Eucalyptus
        - `VNET_DNS` - location of DNS server

    #. Riak CS

        - `RIAKCS_PORT` - the deafult Riak CS port (8080) conflicts with Eucalyptus so this must be changed
        - `STANCHION_HOST` - one node in the Riak CS deployment must also run Stanchion

