from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))

version = '0.0.1'

setup(name='collectd_nfsiostat',
    version=version,
    description="Collectd Plugin to monitor NFS mounts",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Monitoring",
    ],
    keywords='collectd nfsiostat monitoring',
    author='Nacho Barrientos',
    author_email='nacho.barrientos@cern.ch',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
