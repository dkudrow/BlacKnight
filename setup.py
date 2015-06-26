 #!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='blacknight',
      version='0.1.0',
      description='Fault-Management for Cloud Software Appliances',
      url='https://github.com/dkudrow/BlacKnight/',
      author='Daniel Kudrow',
      author_email='dkudrow@cs.ucsb.edu',
      packages=find_packages(),
      install_requires=['kazoo',
                        'PyYAML',
                        'networkx',
                        'Sphinx',
                        'sphinx-rtd-theme'],
      entry_points={'console_scripts': ['blacknight=blacknight:main',
                                        'blacknight-util=blacknight:util']})
