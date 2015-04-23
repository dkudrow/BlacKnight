# puppet/modules/nc/manifests/init.pp

class nc {

  group { 'libvirt' :
    ensure  => 'present',
    members => 'eucalyptus'
  }

  file { '/etc/libvirt/libvirtd.conf' :
    ensure => 'present',
    source => 'puppet:///modules/nc/libvirtd.conf'
  }

  service { 'libvirtd' :
    ensure    => 'running',
    enable    => 'true',
    subscribe => File[ '/etc/libvirt/libvirtd.conf' ]
  }

  file { "$EUCALYPTUS/etc/eucalyptus/eucalyptus.conf" :
    ensure  => 'present',
    content => template('nc/eucalyptus.conf.erb')
  }

  file { "$EUCA_BASE/instances" :
    ensure => 'directory',
    owner  => 'eucalyptus'
  }

}


