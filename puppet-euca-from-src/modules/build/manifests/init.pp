# modules/build/manifests/init.pp

class build {

  $euca_repo = 'https://github.com/eucalyptus/eucalyptus.git'
  $src_deps_url = 'http://www.cs.ucsb.edu/~rich/eucalyptus-src-deps-circa4.0.tgz'
  $src_deps = "$EUCALYPTUS_SRC/eucalyptus-src-deps"

  file { '/etc/profile.d/eucalyptus.sh' :
    content => template('build/eucalyptus.sh.erb'),
    mode   => 0644
  }

  file { '/usr/include/apache2' :
    ensure  => 'link',
    target  => '/usr/include/httpd',
    require => Package[ 'httpd' ]
  }

  vcsrepo { "$EUCALYPTUS_SRC" :
    ensure   => 'present',
    provider => 'git',
    source   => "$euca_repo",
    revision => "$EUCA_TAG",
  }

  exec { 'get WSDL2C.sh' :
    command => 'wget https://raw.github.com/eucalyptus/eucalyptus-rpmspec/master/euca-WSDL2C.sh',
    cwd     => '/opt',
    creates => '/opt/euca-WSDL2C.sh'
  }

}
