# modules/common/manifests/init.pp

class common {

  # TODO: add to group libvirt if in nc
  user { 'eucalyptus' :
    ensure => 'present'
  }

  file { "$EUCA_BASE" :
    ensure => 'directory'
  }

  file { "$EUCALYPTUS" :
    ensure  => 'directory',
  }

}
