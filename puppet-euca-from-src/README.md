## Puppet
### Install puppet
Install puppet with
 
	yum -y install puppet
 
Install the vcsrepo module with

	puppet module install puppetlabs-vcsrepo

Install the packagecloud module (needed for Riak) with

        puppet module install computology-packagecloud

### Customize manifests/site.pp
Define a node in _manifests/site.pp_ for each machine you want to provision. The node definition looks like this:

	# machine's hostname
	node 'scala.cs.ucsb.edu' {
		# the follow two values can be found in
		# /etc/sysconfig/network-scripts/ifcfg-eth1
		$HWADDR = '00:1E:C9:CD:68:3C'
		$UUID = 'ffd70477-49b9-4e7e-a7f2-cf6d6ac98de7'
		# the machines IP address on the private network
		$IPADDR = '10.50.10.25'

		# all machines should get these modules
		include packages
		include network
		include common

		# this module is for machines on which Eucalyptus is being
		# build from source
		include build

		# this module contains head-node specific
		# configuration
		include head

		# this module contains node-controller specific
		# configuration
		include nc
	}

Set the global configuration variables in _manifests/site.pp_.

### Run puppet
Run puppet from the _puppet/_ directory with

	./scripts/run

## Eucalyptus
### Build/install Eucalyptus
If you are building Eucalyptus from scratch, you must do this by hand. In
the EUCALYPTUS_SRC directory:

	./configure '--with-axis2=/usr/share/axis2-*' \
	--with-axis2c=/usr/lib64/axis2c --prefix=$EUCALYPTUS \
	--with-apache2-module-dir=/usr/lib64/httpd/modules \
	--with-db-home=/usr/pgsql-9.1 \
	--with-wsdl2c-sh=/opt/euca-WSDL2C.sh

	make clean; make; make install

### Configure Eucalyptus
Run puppet again to update the newly created configuration files.

	./scripts/run

### Start Eucalyptus
To start the head node

	./scripts/head_config
	./scripts/head_start

To start a worker node

	./scripts/node_config
	./scripts/node_start

##RiakCS
### Notes
* If Riak fails to start with 'node XXX not responding to pings' try deleting the ring with `sudo rm -rf /var/lib/riak/ring/*`
