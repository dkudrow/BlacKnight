# manifests/site.pp

# Puppet
File {
  owner => 'root',
  group => 'root'
}

Exec {
  path => "$path"
}

# Eucalyptus
$CLOUD_OPTS = '--db-home=/usr/pgsql-9.1/ --java-home=/usr/lib/jvm/java-1.7.0'
$EUCALYPTUS = '/'
$EUCA_BASE = '/var/lib/eucalyptus'
$HYPERVISOR = 'kvm'
$LOGLEVEL = 'DEBUG'
$VNET_DNS = '128.111.41.10'
$VNET_MODE = 'MANAGED-NOVLAN'
$VNET_NETMASK = '255.255.255.0'
$VNET_PRIVINTERFACE = 'br0'
$VNET_PUBLICIPS = '128.111.55.41-128.111.55.46 128.111.55.48-128.111.55.49'
$VNET_SUBNET = '10.50.10.0'

# Riak CS
# Note: consult docs.basho.com/riakcs/latest/cookbooks/Version-Compatibility/
# for riak-cs version compatibility
$RIAKCS_VERSION = '2.0.0-1.el6'
$RIAK_VERSION = '2.0.5-1.el6'
$STANCHION_VERSION = '2.0.0'

$RIAKCS_PORT = 9090
$STANCHION_HOST = '128.111.55.39'
$RIAK_ADMIN_KEY = 'GE-NBCXO9KMHB5FX6_LE'
$RIAK_ADMIN_SECRET = 'poijG0ZVojshvgLrkR1CzLmqcHDdekjhoTT5uQ=='

# Define a full installation
$all = ['riak', 'network', 'repo', 'packages', 'config']

# Physical nodes
node 'php.cs.ucsb.edu' {
  $HWADDR ='00:24:E8:6B:7C:E8'
  $UUID ='6f12231d-22c7-47a4-9cf2-b494b60d1f23'
  $PUBLIC_IP = '128.111.55.39'
  $IPADDR = '10.50.10.39'
  $HOSTNAME = 'php.cs.ucsb.edu'

  include riak
  include eucalyptus
  include blacknight
}

node 'oz.cs.ucsb.edu' {
  $HWADDR = '00:26:B9:3D:16:D2'
  $UUID = '99bb00f0-df2b-437b-9b35-1399c3be2ab2'
  $PUBLIC_IP = '128.111.55.51'
  $IPADDR = '10.50.10.51'
  $HOSTNAME = 'oz.cs.ucsb.edu'

  include riak
  include eucalyptus
  include blacknight
}

node 'objc.cs.ucsb.edu' {
  $HWADDR = '00:26:B9:3D:16:D8'
  $UUID = '2755b147-5f3a-4dd8-b408-df050c283421'
  $PUBLIC_IP = '128.111.55.50'
  $IPADDR = '10.50.10.50'
  $HOSTNAME = 'objc.cs.ucsb.edu'

  include riak
  include eucalyptus
  include blacknight
}

node 'scala.cs.ucsb.edu' {
  $HWADDR = '00:1E:C9:CD:68:3C'
  $UUID = 'ffd70477-49b9-4e7e-a7f2-cf6d6ac98de7'
  $PUBLIC_IP = '128.111.55.25'
  $IPADDR = '10.50.10.25'
  $HOSTNAME = 'scala.cs.ucsb.edu'

  include riak
  include eucalyptus
  include blacknight
}
