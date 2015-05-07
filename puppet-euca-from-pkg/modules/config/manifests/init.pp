# modules/config/manifests/init.pp

class config {

  # TODO: chkconfig eucalyptus-* off

  file { '/etc/eucalyptus/eucalyptus.conf' :
    ensure  => file,
    content => template('config/eucalyptus.conf.erb')
  }

  file { '/etc/selinux/config' :
    ensure => file,
    source => 'puppet:///modules/config/selinux.config.original'
  }

  exec { '/usr/sbin/setenforce 0' :
    onlyif => '/usr/sbin/test `/usr/sbin/getenforce` == Enabled'
  }

  service { 'eucalyptus-cloud' :
    enable  => false,
  }

  service { 'eucalyptus-cc' :
    enable  => false,
  }

  service { 'eucalyptus-nc' :
    enable  => false,
  }

  service { 'eucanetd' :
    enable  => false,
  }

}

