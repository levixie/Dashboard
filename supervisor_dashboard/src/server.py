#!/usr/bin/env python
from xmlrpclib import Fault
from urlparse import urlparse
from httplib import CannotSendRequest
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
            for program in self.connection.supervisor.getAllProcessInfo():
                key = "%s:%s" % (program['group'], program['name'])
                program['id'] = key
                program['human_name'] = program['name']
                if program['name'] != program['group']:
                    program['human_name'] = "%s:%s" % (program['group'], program['name'])
                self.status[key] = program
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
