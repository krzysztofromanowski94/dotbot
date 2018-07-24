import dotbot


class Remote(dotbot.Plugin):
    """
    Run plugins on remote machines
    """

    _directive = 'remote'
    _host_list = []

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Remote cannot handle directive %s' % directive)
        return self._process_remote(data)

    def _process_remote(self, data):
        success = True
        print(data)
        self._check_hosts(data)
        return success

    def _check_hosts(self, data):
        if 'hosts' not in data:
            self._log.error("remote: host list can't be empty")
            return False
        for host in data['hosts']:
            if (
                'hostname' not in host and
                'addr' not in host
            ):
                self._log.error("remote: provide 'hostname' or 'addr'")
            if 'password' in host:
                self._log.warning('remote: password in configuration file. '
                                  'Consider adding ssh-key')
        return True
