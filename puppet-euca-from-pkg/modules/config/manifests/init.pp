# modules/config/manifests/init.pp

class config {

  file { "$EUCALYPTUS/etc/eucalyptus/eucalyptus.conf" :
    content => template('config/eucalyptus.conf.erb'),
  }

}
