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
    virtualenv    => '/opt/blacknight',
    url           => 'git+https://github.com/dkudrow/BlacKnight.git',
    owner         => 'root',
    install_args  => ['--force-reinstall'],
   }

  yumrepo { 'cloudera-cdh5' :
    descr    => 'Cloudera\'s Distribution for Hadoop, Version 5',
    baseurl  => 'http://archive.cloudera.com/cdh5/redhat/6/x86_64/cdh/5/',
    gpgkey   => 'http://archive.cloudera.com/cdh5/redhat/6/x86_64/cdh/RPM-GPG-KEY-cloudera',
    gpgcheck => 1
  }

  package { 'zookeeper-server':
    ensure  => 'present',
    require => Yumrepo[ 'cloudera-cdh5' ]
  }

  #service { 'zookeeper-server' :
    #ensure  => 'running',
    #require => Package[ 'zookeeper-server' ]
  #}

}
