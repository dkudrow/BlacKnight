# modules/riak/manifests/init.pp

# NOTE: check Riak version compatibility here:
# http://docs.basho.com/riakcs/latest/cookbooks/Version-Compatibility/

class riak {
  file { '/etc/security/limits.conf' :
    content => template('riak/limits.conf.erb')
  }

  # Riak versions >2.0
  #packagecloud::repo { 'basho/riak' :
  #    type    => 'rpm',
  #}

  #package { 'riak' :
  #  ensure  => 'present',
  #  require => Packagecloud::Repo[ 'basho/riak' ]
  #}

  package { 'riak' :
    ensure   => 'present',
    provider => 'rpm',
    source   => 'http://s3.amazonaws.com/downloads.basho.com/riak/1.4/1.4.12/rhel/6/riak-1.4.12-1.el6.x86_64.rpm',
  }

  file { '/etc/riak/app.config' :
    content => template('riak/riak-app.config.erb'),
    owner   => 'riak',
    group   => 'riak',
    require => Package[ 'riak' ],
  }

  file { '/etc/riak/vm.args' :
    content => template('riak/riak-vm.args.erb'),
    owner   => 'riak',
    group   => 'riak',
    require => Package[ 'riak' ],
  }

  package { 'riak-cs' :
    ensure   => 'present',
    provider => 'rpm',
    source   => 'http://s3.amazonaws.com/downloads.basho.com/riak-cs/1.5/1.5.2/rhel/6/riak-cs-1.5.2-1.el6.x86_64.rpm',
  }

  file { '/etc/riak-cs/app.config' :
    content => template('riak/riak-cs-app.config.erb'),
    owner   => 'riakcs',
    group   => 'riak',
    require => Package[ 'riak-cs' ],
  }

  file { '/etc/riak-cs/vm.args' :
    content => template('riak/riak-cs-vm.args.erb'),
    owner   => 'riakcs',
    group   => 'riak',
    require => Package[ 'riak-cs' ],
  }

  if $IPADDR == $STANCHION {
    package { 'stanchion' :
      ensure   => 'present',
      provider => 'rpm',
      source   => 'http://s3.amazonaws.com/downloads.basho.com/stanchion/1.5/1.5.0/rhel/6/stanchion-1.5.0-1.el6.x86_64.rpm',
    }

    file { '/etc/stanchion/app.config' :
      content => template('riak/stanchion-app.config.erb'),
      owner   => 'stanchion',
      group   => 'riak',
      require => Package[ 'stanchion' ],
    }

    file { '/etc/stanchion/vm.args' :
      content => template('riak/stanchion-vm.args.erb'),
      owner   => 'stanchion',
      group   => 'riak',
      require => Package[ 'stanchion' ],
    }
  }
}
