# manifests/site.pp

# network
$NETWORK = '10.50.10.0'
$NETMASK = '255.255.255.0'

# euca_build
$EUCA_BASE = '/home/opt'
$EUCALYPTUS_SRC = "$EUCA_BASE/eucalyptus"
$EUCA_TAG = 'v4.0.2'
$EUCALYPTUS = "$EUCA_BASE/euca4.0"
$AXIS2C_HOME = "/usr/lib64/axis2c"
$LD_LIBRARY_PATH = "$EUCALYPTUS/packages/axis2c-1.6.0/lib/:$EUCALYPTUS/packages/axis2c-1.6.0/modules/rampart/"

# euca_config
$CLOUD_OPTS = '--db-home=/usr/pgsql-9.1/ --java-home=/usr/lib/jvm/java-1.7.0'
$LOGLEVEL = 'DEBUG'
$HYPERVISOR = 'kvm'
$VNET_MODE = 'MANAGED-NOVLAN'
$VNET_PRIVINTERFACE = 'br0'
$VNET_PUBLICIPS = ''
$VNET_DNS = '128.111.41.10'

# Riak
$STANCHION = '10.50.10.51'

File {
  owner => 'root',
  group => 'root'
}

Exec {
  path => "$path"
}

node 'oz.cs.ucsb.edu' {
  $HWADDR = '00:26:B9:3D:16:D2'
  $UUID = '99bb00f0-df2b-437b-9b35-1399c3be2ab2'
  $PUBLIC_IP = '128.111.55.51'
  $IPADDR = '10.50.10.51'

  include packages
  include network
  include common
  include build
  include head
  include riak
}

node 'objc.cs.ucsb.edu' {
  $HWADDR = '00:26:B9:3D:16:D8'
  $UUID = '2755b147-5f3a-4dd8-b408-df050c283421'
  $PUBLIC_IP = '128.111.55.50'
  $IPADDR = '10.50.10.50'

  include packages
  include network
  include common
  include build
  include head
  include riak
}

node 'scala.cs.ucsb.edu' {
  $HWADDR = '00:1E:C9:CD:68:3C'
  $UUID = 'ffd70477-49b9-4e7e-a7f2-cf6d6ac98de7'
  $PUBLIC_IP = '128.111.55.25'
  $IPADDR = '10.50.10.25'

  include packages
  include network
  include common
  include build
  include nc
}
