## Puppet
### Install puppet
Install puppet with
 
	yum -y install puppet

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

## Riak CS

### Starting Riak CS
As root, run the following on the first node

	riak start
	stanchion start
	riak-cs start
	
On each other node that is to be part of the Riak cluster run

	riak start
	riak-cs start
	riak-admin cluster join <nodename_of_first_node>
	riak-admin plan
	riak-admin comit
	
### Generating user credentials

### Notes
* If Riak fails to start with 'node XXX not responding to pings' try deleting the ring with `sudo rm -rf /var/lib/riak/ring/*`
