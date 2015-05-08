# puppet/modules/packages/manifests/init.pp

class packages {

  $pkgs = [ 'ntp', 'eucalytpus-nc', 'eucalytpus-cloud', 'eucalyptus-cc',
            #'eucalyptus-imaging-worker-image', 'eucalyptus-load-balancer-image',
            'eucalyptus-sc', 'eucalyptus-walrus' ]

  package { $pkgs :
    ensure  => 'present'
  }

}
