#!/usr/bin/env python
from xmlrpclib import ServerProxy, Fault
from urlparse import urlparse

from django.utils.datastructures import SortedDict

class Server(object):
    def __init__(self, connection_string, sid):
        self.name = urlparse(connection_string).hostname
        self.connection = ServerProxy(connection_string)
        self.status = SortedDict()
        self.sid = sid

    def refresh1(self):
        try:
            for process in self.connection.supervisor.getAllProcessInfo():
                key = "%s:%s" % (process['group'], process['name'])
                process['id'] = key
                process['human_name'] = process['name']
                if process['name'] != process['group']:
                    process['human_name'] = "%s:%s" % (process['group'], process['name'])
                self.status[key] = process
        except Fault, e:
            return False

    def refresh(self):
        self.status = SortedDict(("%s:%s" % (i['group'], i['name']), i) for i in self.connection.supervisor.getAllProcessInfo())
        for key, program in self.status.items():
            program['id'] = key
            program['human_name'] = program['name']
            if program['name'] != program['group']:
                program['human_name'] = "%s:%s" % (program['group'], program['name'])

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
