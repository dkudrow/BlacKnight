 #!/usr/bin/env python

import setuptools

setuptools.setup(
      name='blacknight',
      version='0.1.0',
      description='Fault-Management for Cloud Software Appliances',
      url='https://github.com/dkudrow/BlacKnight/',
      author='Daniel Kudrow',
      author_email='dkudrow@cs.ucsb.edu',
      # license='',
      packages=setuptools.find_packages(),
      install_requires=['kazoo', 'PyYAML', 'networkx', 'Sphinx', 'sphinx-rtd-theme'],
      # package_data=[],
      # data_files=[],
      )
