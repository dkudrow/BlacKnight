# modules/blacknight/manifests/init.pp

class blacknight {

  # We are using a PyPy virtualenv to run BlacKnight because there is no
  # reliable Python 2.7 package for CentOS 6...
  class { 'python' :
    version    => 'pypy',
    virtualenv => true
  }

  python::virtualenv { '/opt/BlacKnight/venv' :
    ensure     => 'present',
    version    => 'pypy',
    owner      => 'root',
    group      => 'root',

    # Setting virtualenv directly is a bit of a hack - the class is supposed to
    # infer the correct virtualenv command from the version attribute but this
    # appears to be broken
    virtualenv => 'virtualenv -p pypy'
  }

  python::pip { 'blacknight' :
    pkgname       => 'blacknight',
    ensure        => 'latest',
    virtualenv    => '/opt/BlacKnight/venv',
    url           => 'git+https://github.com/dkudrow/BlacKnight.git',
    owner         => 'root',
    install_args  => ['--force-reinstall'],
   }

  class { 'zookeeper' :
    repo => 'cloudera',
    packages => [ 'zookeeper', 'zookeeper-server' ],
    service_name         => 'zookeeper-server',
    initialize_datastore => true,
    servers => $ZK_SERVERS
  }

}
