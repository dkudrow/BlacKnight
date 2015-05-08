# modules/riak/manifests/init.pp

class riak {

  packagecloud::repo { ['basho/riak', 'basho/riak-cs'] :
    type => 'rpm'
  }

  package { 'riak' :
    ensure  => $RIAK_VERSION,
    require => Packagecloud::Repo['basho/riak'],
    before  => Package['riak-cs']
  }
  
  file { '/etc/riak/riak.conf' :
    content => template('riak/riak.conf.erb'),
    owner   => 'riak',
    group   => 'riak',
    require => Package['riak']
  }

  file { '/etc/riak/advanced.config' :
    content => template('riak/advanced.config.erb'),
    owner   => 'riak',
    group   => 'riak',
    require => Package['riak']
  }

  package { 'riak-cs' :
    ensure  => $RIAKCS_VERSION,
    require => Packagecloud::Repo['basho/riak-cs'],
  }

  file { '/etc/riak-cs/riak-cs.conf' :
    content => template('riak/riak-cs.conf.erb'),
    owner   => 'riakcs',
    group   => 'riak',
    require => Package['riak-cs']
  }

  if $IPADDR == $STANCHION_HOST or $PUBLIC_IP == $STANCHION_HOST {

    # Stanchion 2.0 hasn't made it to packagecloud yet...
    #package { 'stanchion' :
    #ensure  => $STANCHION_VERSION,
    #require => Packagecloud::Repo['basho/riak-cs']
    #}

    # ...so in the meantime install from the rpm.
    package { 'stanchion' :
      provider => rpm,
      ensure   => present,
      source   => 'http://s3.amazonaws.com/downloads.basho.com/stanchion/2.0/2.0.0/rhel/6/stanchion-2.0.0-1.el6.x86_64.rpm'
    }

    file { '/etc/stanchion/stanchion.conf' :
      content => template('riak/stanchion.conf.erb'),
      owner   => 'stanchion',
      group   => 'riak',
      require => Package['stanchion']
    }
  }

  file { '/etc/security/limits.conf' :
    content => template('riak/limits.conf.erb')
  }

  #file { '/etc/riak/app.config' :
    #content => template('riak/riak-app.config.erb'),
    #owner   => 'riak',
    #group   => 'riak',
    #require => Package[ 'riak' ],
  #}

  #file { '/etc/riak/vm.args' :
    #content => template('riak/riak-vm.args.erb'),
    #owner   => 'riak',
    #group   => 'riak',
    #require => Package[ 'riak' ],
  #}

  #file { '/etc/riak-cs/app.config' :
    #content => template('riak/riak-cs-app.config.erb'),
    #owner   => 'riakcs',
    #group   => 'riak',
    #require => Package[ 'riak-cs' ],
  #}

  #file { '/etc/riak-cs/vm.args' :
    #content => template('riak/riak-cs-vm.args.erb'),
    #owner   => 'riakcs',
    #group   => 'riak',
    #require => Package[ 'riak-cs' ],
  #}

  #if $IPADDR == $STANCHION {
    #package { 'stanchion' :
      #ensure   => 'present',
      #provider => 'rpm',
      #source   => 'http://s3.amazonaws.com/downloads.basho.com/stanchion/1.5/1.5.0/rhel/6/stanchion-1.5.0-1.el6.x86_64.rpm',
    #}

    #file { '/etc/stanchion/app.config' :
      #content => template('riak/stanchion-app.config.erb'),
      #owner   => 'stanchion',
      #group   => 'riak',
      #require => Package[ 'stanchion' ],
    #}

    #file { '/etc/stanchion/vm.args' :
      #content => template('riak/stanchion-vm.args.erb'),
      #owner   => 'stanchion',
      #group   => 'riak',
      #require => Package[ 'stanchion' ],
    #}
  #}
}
