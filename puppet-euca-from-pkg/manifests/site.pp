# manifests/site.pp

# network
$NETWORK = '10.50.10.0'
$NETMASK = '255.255.255.0'

# config
$EUCALYPTUS = '/'
$EUCA_BASE = '/var/lib/eucalyptus'
$CLOUD_OPTS = '--db-home=/usr/pgsql-9.1/ --java-home=/usr/lib/jvm/java-1.7.0'
$LOGLEVEL = 'DEBUG'
$HYPERVISOR = 'kvm'
$VNET_MODE = 'MANAGED-NOVLAN'
$VNET_PRIVINTERFACE = 'br0'
$VNET_PUBLICIPS = '128.111.55.41-128.111.55.46 128.111.55.48-128.111.55.49'
$VNET_DNS = '128.111.41.10'

# riak
# Note: consult docs.basho.com/riakcs/latest/cookbooks/Version-Compatibility/
# for riak-cs version compatibility
$RIAKCS_VERSION = '2.0.0-1.el6'
$RIAK_VERSION = '2.0.5-1.el6'
$STANCHION_VERSION = '2.0.0'

$RIAK_HOST_PORT = '8087'
$RIAK_LISTEN_PORT = '9090'
$STANCHION_HOST = '128.111.55.39'
$STANCHION_PORT = '8085'

File {
  owner => 'root',
  group => 'root'
}

Exec {
  path => "$path"
}

node 'php.cs.ucsb.edu' {
  $HWADDR ='00:24:E8:6B:7C:E8'
  $UUID ='6f12231d-22c7-47a4-9cf2-b494b60d1f23'
  $PUBLIC_IP = '128.111.55.39'
  $IPADDR = '10.50.10.39'
  $HOSTNAME = 'php.cs.ucsb.edu'

  include riak
  include network
  include repo
  include packages
  include config
}

node 'oz.cs.ucsb.edu' {
  $HWADDR = '00:26:B9:3D:16:D2'
  $UUID = '99bb00f0-df2b-437b-9b35-1399c3be2ab2'
  $PUBLIC_IP = '128.111.55.51'
  $IPADDR = '10.50.10.51'
  $HOSTNAME = 'oz.cs.ucsb.edu'

  include riak
  include network
  include repo
  include packages
  include config
}

node 'objc.cs.ucsb.edu' {
  $HWADDR = '00:26:B9:3D:16:D8'
  $UUID = '2755b147-5f3a-4dd8-b408-df050c283421'
  $PUBLIC_IP = '128.111.55.50'
  $IPADDR = '10.50.10.50'
  $HOSTNAME = 'objc.cs.ucsb.edu'

  include riak
  include network
  include repo
  include packages
  include config
}

node 'scala.cs.ucsb.edu' {
  $HWADDR = '00:1E:C9:CD:68:3C'
  $UUID = 'ffd70477-49b9-4e7e-a7f2-cf6d6ac98de7'
  $PUBLIC_IP = '128.111.55.25'
  $IPADDR = '10.50.10.25'
  $HOSTNAME = 'scala.cs.ucsb.edu'

  include riak
  include network
  include repo
  include packages
  include config
}
