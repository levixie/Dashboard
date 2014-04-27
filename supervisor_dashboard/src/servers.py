#!/usr/bin/env python
from django.conf import settings
from django.utils.datastructures import SortedDict

from src.server import Server

class Servers(object):
    def __init__(self):
        self.servers = SortedDict()
        fp = open(settings.CONFIG_FILE)
        index = 0
        for line in fp:
            sid = str(index)
            server = Server(line.strip(), sid=sid)
            self.servers[sid] = server
            index += 1
        fp.close()

    def refresh(self):
        for s in self.servers.values():
            s.refresh()

    def stop(self, name):
        for s in self.servers.values():
            s.stop(name)

    def start(self, name):
        for s in self.servers.values():
            s.start(name)

    def restart(self, name):
        for s in self.servers.values():
            s.restart(name)

    def start_all(self):
        for s in self.servers.values():
            s.start_all()
