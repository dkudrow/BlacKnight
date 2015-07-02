# modules/blacknight/manifests/init.pp

class blacknight {

  # Note: we will use cloudera's ZooKeeper rpm for simplicity
  package { 'python-pip', 'cloudera-cdh4' :
    ensure 'present'
  }

  package { 'bkacknight' :
    provider => 'pip',
    ensure   => 'present',
    source   => '../../../../'
    require  => Package[ 'python-pip' ]
  }

  package { 'zookeeper-server':
    ensure  => 'present',
    require => Package[ 'cloudera-cdh4' ]
  }

  service {'zookeeper-server' :
    ensure  => 'running',
    require => Package[ 'zookeeper-server' ]
  }

}