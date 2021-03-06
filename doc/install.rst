Installation
============

This section describes the installation of BlacKnight as well as that of a test environment based on Eucalyptus. A Puppet manifest is provided in the ``puppet/`` directory to make this process marginally less painful. This manifest is not perfect - installation requires some supervision and, in certain cases, multiple passes. To ensure that all necessary components are installed run Puppet repeatedly until no messages are printed. Familiarity with puppet is not necessary (you can simply follow the instructions below) but will be helpful for trouble-shooting and required for contributing.

All development was done on CentOS 6.6 (final) and determining whether BlacKnight will run in another environment is left as an exercise for the (motivated) reader.


Puppet
------

#. Install Puppet on all hosts.

    .. code-block:: shell

        yum install rubygems
        gem install puppet -v '3.8.1'
        puppet module install computology-packagecloud
        puppet module install stankevich-python
        puppet module install deric-zookeeper


.. note::

    Configuration of the installation is handled entirely within ``puppet/manifests/site.pp``. Deployment-wide configuration is managed using global variables which are inherited by all hosts. Each host is declared in a *node* block; this block contains host-specific information (e.g. IP address, &c.) and several *include* directives that indicate which modules should be applied to the host. Use the code sample below to adapt ``site.pp`` to your deployment.

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

#. Set the following global configuration variables in ``site.pp``.

    * **$ZK_SERVERS**: list of all hosts in the appliance
    * **$ZK_IDS**: hash of hosts in appliance to their positions in the array above

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

#. On the remaining nodes start Riak with the following commands. The nodename of the stanchion node can be found in ``/etc/riak/riak.conf``.

    .. code-block:: shell

        riak start
        riak-cs start
        riak-admin cluster join riak@<nodename_of_stanchion_node>
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

.. tip::

    If this is the first time you are configuring this machine you should restart it to bring up the bridge interface.

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

#. Distribute keys across all hosts.

    a. Generate an ssh key on each host.

        .. code-block:: shell

            [ -e /root/.ssh/id_rsa ] || ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa

    b. Add every host's key to each other's list of authorized hosts.

        .. code-block:: shell

            for host in hosts; do
                # You will get very good at typing your password...
                cat $(ssh host 'cat /root/.ssh/id_rsa') >> /root/.ssh/authorized_hosts
            done

Development
-----------

BlacKnight comes equipped with a series of utilities for simulated execution as testing on a full scale appliance can be unwieldy. The **zkconf** tool is extremely useful for quickly deploying temporary ZooKeeper ensembles locally; it can be found at https://github.com/phunt/zkconf and the instructions for its use are straightforward. The :mod:`util` contains various commands for communicating with the ZooKeeper server to simulate events and services. The provided specification (``test/spec.yaml``) simply points hooks at blacknight-util to start and stop simulated services.


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
