# puppet/modules/packages/manifests/init.pp

class packages {

  $epel = 'http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm'
  $elrepo = 'http://elrepo.org/linux/elrepo/el6/x86_64/RPMS/elrepo-release-6-5.el6.elrepo.noarch.rpm'
  $pgdg91 = 'http://yum.pgrpms.org/9.1/redhat/rhel-6-x86_64/pgdg-centos91-9.1-4.noarch.rpm'

  $pkgs_nogpg = [

    'axis2-adb', 'axis2-adb-codegen', 'axis2-codegen',
    'axis2c-devel', 'postgresql91', 'postgresql91-server', 'axis2c',
    'rampartc', 'rampartc-devel', 'velocity'

  ]

  $pkgs = [

    'ntp', 'httpd-devel', 'ant', 'ant-nodeps', 'libcurl-devel',
    'gawk', 'git', 'java-1.6.0-openjdk-devel', 'gcc', 'make', 'apache-ivy',
    'bridge-utils', 'coreutils', 'curl', 'dejavu-serif-fonts',
    'device-mapper', 'dhcp', 'kmod-drbd83', 'drbd83-utils', 'e2fsprogs',
    'euca2ools', 'file', 'httpd', 'iptables', 'iscsi-initiator-utils',
    'java-1.7.0-openjdk', 'java-1.7.0-openjdk-devel', 'jpackage-utils',
    'PyGreSQL', 'libcurl', 'libvirt', 'libvirt-devel', 'libxml2-devel',
    'libxslt-devel', 'lvm2', 'm2crypto', 'openssl-devel', 'parted',
    'patch', 'perl-Crypt-OpenSSL-RSA', 'perl-Crypt-OpenSSL-Random',
    'python-boto', 'python-devel', 'python-setuptools', 'rsync',
  'scsi-target-utils', 'sudo', 'swig', 'util-linux-ng', 'vconfig',
  'vtun', 'wget', 'which', 'xalan-j2-xsltc', 'ipset', 'ebtables', 'bc'

  ]

  exec { 'install epel' :
    command => "yum -y install $epel",
    creates => '/etc/yum.repos.d/epel.repo',
    before => [ Package[ $pkgs ], Package[ $pkgs_nogpg ] ]
  }

  exec { 'install elrepo' :
    command => "yum -y install $elrepo",
    creates => '/etc/yum.repos.d/elrepo.repo',
    before => [ Package[ $pkgs ], Package[ $pkgs_nogpg ] ]
  }

  exec { 'install pgdg91' :
    command => "yum -y install $pgdg91",
    creates => '/etc/yum.repos.d/pgdg-91-centos.repo',
    before => [ Package[ $pkgs ], Package[ $pkgs_nogpg ] ]
  }

  yumrepo { 'euca-4.0' :
    enabled  => 1,
    baseurl  => 'http://downloads.eucalyptus.com/software/eucalyptus/4.0/centos/$releasever/$basearch',
    descr    => 'Eucalyptus',
    gpgcheck => 0,
    before   => [ Package[ $pkgs ], Package[ $pkgs_nogpg ] ]
  }

  yumrepo { 'euca-build-deps' :
    enabled  => 1,
    baseurl  => 'http://downloads.eucalyptus.com/software/eucalyptus/build-deps/3.4/centos/$releasever/$basearch',
    descr    => 'Eucalyptus build dependencies',
    gpgcheck => 0,
    before   => [ Package[ $pkgs ], Package[ $pkgs_nogpg ] ]
  }

  yumrepo { 'euca2tools-3.1' :
    enabled  => 1,
    baseurl  => 'http://downloads.eucalyptus.com/software/euca2ools/3.1/centos/$releasever/$basearch',
    descr    => 'Euca2tools',
    gpgcheck => 0,
    before   => [ Package[ $pkgs ], Package[ $pkgs_nogpg ] ]
  }

  package { $pkgs :
    ensure  => 'present'
  }

  package { $pkgs_nogpg :
    ensure          => 'present',
    install_options => [ '--nogpgcheck' ]
  }
}
