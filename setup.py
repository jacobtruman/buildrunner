"""
Copyright (C) 2014 Adobe
"""
from setuptools import setup, find_packages
import vcsinfo

#pylint: disable=C0301
setup(
    name='buildrunner',
    version='0.4',
    author='***REMOVED***',
    author_email="***REMOVED***",
    license="Adobe",
    url="https://***REMOVED***/***REMOVED***/buildrunner",
    description="",
    long_description="",

    packages=find_packages(),
    scripts=[
        'bin/buildrunner',
    ],
    package_data={
        'buildrunner' : ['SourceDockerfile'],
        'buildrunner.sshagent' : [
            'SSHAgentProxyImage/Dockerfile',
            'SSHAgentProxyImage/run.sh',
            'SSHAgentProxyImage/login.sh',
        ],
    },
    install_requires=[
        'PyYAML==3.11',
        'requests==2.9.1',
        'paramiko==1.16.0',
        'pycrypto==2.6.1',
        'docker-py==1.3.1',
        'vcsinfo>=0.1.23',
        'fabric==1.10.1',
        'Jinja2==2.7.3',
    ],

    # override the default egg_info class to enable setting the tag_build
    cmdclass={
        'egg_info': vcsinfo.VCSInfoEggInfo,
    },
)
