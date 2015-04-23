# modules/repo/manifests/init.pp

class repo {

  package { 'eucalyptus-release' :
    provider => rpm,
    ensure   => present,
    source   => 'http://downloads.eucalyptus.com/software/eucalyptus/4.1/centos/6/x86_64/eucalyptus-release-4.1.el6.noarch.rpm'
  }

  package { 'euca2ools-release' :
    provider => rpm,
    ensure   => present,
    source   => 'http://downloads.eucalyptus.com/software/euca2ools/3.2/centos/6/x86_64/euca2ools-release-3.2.el6.noarch.rpm'
  }

  package { 'epel-release' :
    provider => rpm,
    ensure   => present,
    source   => 'http://downloads.eucalyptus.com/software/eucalyptus/4.1/centos/6/x86_64/epel-release-6.noarch.rpm'
  }

}
