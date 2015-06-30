# modules/blacknight/manifests/init.pp

class blacknight {
  package { 'bkacknight' :
    provider => 'pip',
    ensure   => 'present',
    source   => '../../../../'
  }
}