import os
import socket

import dotbot
import getpass
import paramiko
import pprint


class Remote(dotbot.Plugin):
    """
    Run plugins on remote machines
    """

    # type(exception).__name__

    _directive = 'remote'
    _host_list = []
    _ssh_config = None

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Remote cannot handle directive %s' % directive)
        return self._process_remote(data)

    def _process_remote(self, data):
        success = True
        print(data)

        self._ssh_config = paramiko.SSHConfig()
        user_config_file = os.path.expanduser("~/.ssh/config")
        if os.path.exists(user_config_file):
            with open(user_config_file) as f:
                self._ssh_config.parse(f)

        self._check_hosts(data)

        pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self._host_list)

        for host in self._host_list:
            pp.pprint(host)

        return success

    def _check_hosts(self, data):
        if 'hosts' not in data:
            self._log.error("remote: host list can't be empty")
            return False
        for host in data['hosts']:
            hostname = None
            user = None
            addr = None
            password = None
            identityfile = None
            host_config = None
            debug_name = None
            connection_types = []

            if 'hostname' in host:
                hostname = host['hostname']
                host_config = self._ssh_config.lookup(hostname)
                debug_name = hostname
                # Check if system is able to resolve hostname
                try:
                    addr = socket.gethostbyname(hostname)
                    connection_types.append('addr')
                except socket.gaierror:
                    # host_config is { 'hostname': 'something' }
                    if len(host_config) == 1:
                        try:
                            addr = socket.gethostbyname(host_config['hostname'])
                            connection_types.append('addr')
                        except socket.gaierror:
                            self._log.debug('No address associated with `%s`.' % hostname)
                            hostname = None

                    elif len(host_config) <= 0:
                        pass
                        host_config = None

                    else:
                        connection_types.append('ssh_config')

            if (
                'addr' in host and
                addr is None
            ):
                addr = host['addr']
                if debug_name is None:
                    debug_name = addr
                try:
                    addr = socket.gethostbyname(addr)
                    connection_types.append('addr')
                except socket.gaierror:
                    self._log.debug('No address associated with `%s`.' % debug_name)
                    addr = None

            if (
                addr is None and
                hostname is None
            ):
                self._log.error("Can't find host `%s`" % debug_name)
                continue

            if 'user' not in host:
                try:
                    user = host_config['user']
                except KeyError:
                    self._log.debug("User not set in ssh_config for `%s`." % debug_name)
                except TypeError:
                    self._log.debug("No entry in ssh_config for `%s`." % debug_name)

                # noinspection PyBroadException
                try:
                    user = getpass.getuser()
                except Exception:
                    self._log.error("Can't get username. Please provide"
                                    "`user` key in configuration file for address %s"
                                    % addr)
            else:
                user = host['user']

            # Having password in file is generally not recommended, but sometimes useful
            if 'password' in host:
                password = host['password']
                self._log.warning("remote: password in configuration file. "
                                  "Consider adding ssh-key for `%s`" % debug_name)
                # ToDo: from ssh_config

            print(debug_name)
            if 'identityfile' in host:
                identityfile = host['identityfile']

            self._host_list.append({})
            self._host_list[-1]['hostname'] = hostname
            self._host_list[-1]['addr'] = addr
            self._host_list[-1]['user'] = user
            self._host_list[-1]['password'] = password
            self._host_list[-1]['identityfile'] = identityfile
            self._host_list[-1]['host_config'] = host_config

        return True
