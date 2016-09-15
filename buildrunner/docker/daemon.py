"""
Copyright (C) 2016 Adobe
"""
from __future__ import absolute_import
import os

from buildrunner.docker import DOCKER_DEFAULT_DOCKERD_URL


class DockerDaemonProxy(object):
    """
    Class used to encapsulate Docker daemon information within a container.
    """


    def __init__(self, docker_client, log):
        """
        """
        self.docker_client = docker_client
        self.log = log
        self._daemon_container = None
        self._env = {
            'DOCKER_HOST': DOCKER_DEFAULT_DOCKERD_URL,
        }


    def get_info(self):
        """
        Return a tuple where the first item is the daemon container id and
        the second is a dict of environment variables to be injected into other
        containers providing settings for docker clients to connect to the
        encapsulated daemon.
        """
        return (self._daemon_container, self._env)


    def start(self):
        """
        Starts a Docker container encapsulating information to connect to the
        current docker daemon.
        """
        _volumes = []
        _binds = {}

        # setup docker env and mounts so that the docker daemon is accessible
        # from within the run container
        for env_name, env_value in os.environ.iteritems():
            if env_name == 'DOCKER_HOST':
                self._env['DOCKER_HOST'] = env_value
            if env_name == 'DOCKER_TLS_VERIFY' and env_value:
                self._env['DOCKER_TLS_VERIFY'] = '1'
            if env_name == 'DOCKER_CERT_PATH':
                if os.path.exists(env_value):
                    _volumes.append('/dockerdaemon/certs')
                    _binds[env_value] = {
                        'bind': '/dockerdaemon/certs',
                        'ro': True,
                    }
                    self._env['DOCKER_CERT_PATH'] = '/dockerdaemon/certs'

        # if DOCKER_HOST is a unix socket we need to mount the socket in the
        # container and adjust the DOCKER_HOST variable accordingly
        docker_host = self._env['DOCKER_HOST']
        if docker_host.startswith('unix://'):
            # need to map the socket as a volume
            local_socket = docker_host.replace('unix://', '')
            if os.path.exists(local_socket):
                _volumes.append('/dockerdaemon/docker.sock')
                _binds[local_socket] = {
                    'bind': '/dockerdaemon/docker.sock',
                    'ro': False,
                }
                self._env['DOCKER_HOST'] = 'unix:///dockerdaemon/docker.sock'

        # create and start the Docker container
        self._daemon_container = self.docker_client.create_container(
            'busybox',
            command='/bin/sh',
            volumes=_volumes,
        )['Id']
        self.docker_client.start(
            self._daemon_container,
            binds=_binds,
        )
        self.log.write(
            "Created Docker daemon container %.10s\n" % self._daemon_container
        )


    def stop(self):
        """
        Stops the Docker daemon container.
        """
        # kill container
        self.log.write(
            "Destroying Docker daemon container %.10s\n" % (
                self._daemon_container,
            )
        )
        if self._daemon_container:
            self.docker_client.remove_container(
                self._daemon_container,
                force=True,
                v=True,
            )