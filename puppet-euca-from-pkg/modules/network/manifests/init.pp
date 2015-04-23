# puppet/modules/network/manifests/init.pp

class network {

  file { '/etc/sysconfig/network-scripts/ifcfg-br0' :
    content => template('network/ifcfg-br0.erb'),
    mode    => 0644
  }

  file { '/etc/sysconfig/network-scripts/ifcfg-eth1' :
    content => template('network/ifcfg-eth1.erb'),
    mode    => 0644
  }

  service { 'ntpd' :
    require => Package[ 'ntp' ],
    ensure  => 'running',
    enable  => 'true'
  }

  service { 'iptables' :
    ensure => 'stopped',
    enable => 'false'
  }

  # hackosaurus rex
  exec { 'Bring up br0 at boot':
    command => "/bin/echo 'ifup br0' >> /etc/rc.local",
    unless  => "/bin/grep 'ifup br0' /etc/rc.local"
  }
}
