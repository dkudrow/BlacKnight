# modules/head/manifests/init.pp

class head {

  package { 'eucalyptus-load-balancer-image' :
    ensure => 'present'
  }

  file { "$EUCALYPTUS/etc/eucalyptus/eucalyptus.conf" :
    content => template('head/eucalyptus.conf.erb'),
    require => File[ "$EUCALYPTUS" ]
  }

  file { "$EUCA_BASE/db" :
    ensure => 'directory',
    owner  => 'eucalyptus'
  }

  file { "$EUCALYPTUS/db" :
    ensure  => 'link',
    target  => "$EUCA_BASE/db",
    require => File[ "$EUCALYPTUS", "$EUCA_BASE/db" ]
  }

  file { "$EUCA_BASE/bukkits" :
    ensure => 'directory',
    owner  => 'eucalyptus'
  }

  file { "$EUCALYPTUS/bukkits" :
    ensure => 'link',
    target => "$EUCA_BASE/bukkits",
    require => File[ "$EUCALYPTUS", "$EUCA_BASE/bukkits" ]
  }

  file { "$EUCA_BASE/volumes" :
    ensure => 'directory',
    owner  => 'eucalyptus'
  }

  file { "$EUCALYPTUS/volumes" :
    ensure => 'link',
    target => "$EUCA_BASE/volumes",
    require => File[ "$EUCALYPTUS", "$EUCA_BASE/volumes" ]
  }

  file { '/root/cred' :
    ensure => 'directory'
  }

}
