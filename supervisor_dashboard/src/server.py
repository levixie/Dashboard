#!/usr/bin/env python
from xmlrpclib import Fault
from urlparse import urlparse
import socket

from django.utils.datastructures import SortedDict

from src.timeout_server_proxy import TimeoutServerProxy

class Server(object):
    def __init__(self, connection_string, sid):
        self.name = urlparse(connection_string).hostname
        self.connection = TimeoutServerProxy(connection_string, timeout=2)
        self.status = SortedDict()
        self.sid = sid

    def refresh(self):
        try:
            self.status = SortedDict()
            for process in self.connection.supervisor.getAllProcessInfo():
                key = "%s:%s" % (process['group'], process['name'])
                process['id'] = key
                process['human_name'] = process['name']
                if process['name'] != process['group']:
                    process['human_name'] = "%s:%s" % (process['group'], process['name'])
                self.status[key] = process
        except (Fault, socket.timeout):
            return False
        except:
            return False

    def stop(self, name):
        try:
            return self.connection.supervisor.stopProcess(name)
        except Fault, e:
            if e.faultString.startswith('NOT_RUNNING'):
                return False
            raise

    def start(self, name):
        try:
            return self.connection.supervisor.startProcess(name)
        except Fault, e:
            if e.faultString.startswith('ALREADY_STARTED'):
                return False
            raise

    def start_all(self):
        return self.connection.supervisor.startAllProcesses()

    def restart(self, name):
        self.stop(name)
        return self.start(name)
