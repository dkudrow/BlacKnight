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

#. In ``site.pp``, add the following line to each host on which BlacKnight should be installed.

    .. code-block:: ruby

        include blacknight

#. Apply the manifest by running the following commands as root on each host.

    .. code-block:: shell

        cd puppet/
        ./run_puppet

.. warning::

    Puppet occasionally has trouble creating virtualenvs with pypy. If you see an error along the lines of ``virtualenv-pypy: command not found``, you will have to create the virtualenv yourself with

    .. code-block:: shell

        virtualenv -p pypy /opt/blacknight

RiakCS
------

#. Set the following global configuration variables in ``site.pp``.

    * **$STANCHION_HOST**: IP address of the host that will run Stanchion (can be any host)
    * **$RIAK_ADMIN_KEY**: admin-key
    * **$RIAK_ADMIN_SECRET**: admin-secret

#. Apply the manifest by running the following commands as root on the Stanchion host.

    .. code-block:: shell

        cd puppet/
        ./run_puppet

#. Start RiakCS by running the following commands as root on the Stanchion host.

    .. code-block:: shell

        riak start
        stanchion start
        riak-cs start

#. Manually edit the RiakCS configuration file ``/etc/riak-cs/riak-cs.conf`` by changing

    .. code-block:: properties

        anonymous_user_creation = off

    to

    .. code-block:: properties

        anonymous_user_creation = on

#. Restart Riak by by running

    .. code-block:: shell

        riak-cs restart

#. Create an admin user by running the following command. Use the value of ``$RIAKCS_PORT`` in ``site.pp`` as the port in the URL. The choice of name and email for the admin user are not terribly important.

    .. code-block:: shell

        curl -XPOST http://localhost:9090/riak-cs/user \
            -H 'Content-Type: application/json' \
            -d '{"email":"admin@admin.com", "name":"admin"}'

#. RiakCS should respond with the key and secret of the admin user. Copy these into ``$RIAK_ADMIN_KEY`` and ``$RIAK_ADMIN_SECRET`` respectively in ``site.pp``.

#. Repeat step 2 on the remaining hosts.

#. Restart Riak on the Stanchion host as per step 6.

#. On the remaining nodes start Riak with the following commands. The nodename of stanchion node is

    .. code-block:: shell

    riak start
    riak-cs start
    riak-admin cluster join riak@<hostname_of_stanchion_node>
    riak-admin plan
    riak-admin commit

.. warning::

    In the following line of ``/etc/riak/advanced.config``,

    .. code-block:: erlang

          {add_paths, ["/usr/lib64/riak-cs/lib/riak_cs-2.0.1/ebin"]},

    the version string (*2.0.1* above) must match the installed verson of RiakCS or Riak will not start!


Eucalyptus
----------

#. Set the following global configuration variables in ``site.pp``. (These all mirror variables in *eucalyptus.conf*)

    * **$VNET_DNS**: IP address of local DNS server (if applicable)
    * **$VNET_NETMASK**: subnet mask for bridged network
    * **$VNET_PRIVINTERFACE**: name interface to bridged network
    * **$VNET_PUBLICIPS**: available public IP addresses
    * **$VNET_SUBNET**: subnet of bridged network

#. Apply the manifest by running the following commands as root on all hosts.

    .. code-block:: shell

        cd puppet/
        ./run_puppet

#. Choose one host to be the initial primary head and start the head node components on this host.

    .. code-block:: shell

        # on the primary
        rm -rf /var/lib/eucalyptus/db/
        euca_conf --initialize
        service eucalyptus-cloud start
        # wait until CLC is up (check /var/log/eucalyptus/cloud-output.log)
        service eucalyptus-cc start

#. Register components on the primary head.

    .. code-block:: shell

        # on the primary
        euca_conf --register-service -T user-api -H <primary_ip> -N <primary_hostname>-api
        euca_conf --register-cluster -P <partition> -H <primary_ip> -C <primary_hostname>-cc
        euca_conf --register-sc -P <partition> -H <primary_ip> -C <primary_hostname>-sc

#. Generate admin user credentials.

    .. code-block:: shell

        euca_conf --get-credentials admin.zip
        unzip admin.zip -d /root/cred/
        source /root/cred/eucarc

#. Configure primary head. Any host can be used as the RiakCS endpoint.

    .. code-block:: shell

        # block storage
        euca-modify-property -p <partition>.storage.blockstoragemanager=overlay

        # object storage
        euca-modify-property -p objectstorage.providerclient=riakcs
        euca-modify-property -p objectstorage.s3provider.s3endpoint=<riakcs_ip>:9090
        euca-modify-property -p objectstorage.s3provider.s3accesskey=<riakcs_admin_key>
        euca-modify-property -p objectstorage.s3provider.s3secretkey=<riakcs_admin_secret>

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
