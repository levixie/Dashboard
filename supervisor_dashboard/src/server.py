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
        self.connection_string = connection_string

    def refresh(self):
        try:
            status = SortedDict()
            for program in self.connection.supervisor.getAllProcessInfo():
                key = "%s:%s" % (program['group'], program['name'])
                program['id'] = key
                program['human_name'] = program['name']
                if program['name'] != program['group']:
                    program['human_name'] = "%s:%s" % (program['group'], program['name'])
                status[key] = program
            self.status = status    
            return True
        except (Fault, socket.timeout):
            return False
        except:
            return False

    def stop(self, name, wait=True):
        try:
            self.connection.supervisor.stopProcess(name, wait)
            return True
        except Fault, e:
            return False

    def start(self, name, wait=True):
        try:
            self.connection.supervisor.startProcess(name, wait)
            return True
        except Fault, e:
            return False

    def start_all(self, wait=True):
        try:
            self.connection.supervisor.startAllProcesses(wait)
            return True
        except Fault,e:
            print e
            return False

    def stop_all(self, wait=True):
        try:
            self.connection.supervisor.stopAllProcesses(wait)
            return True
        except Fault,e:
            print e
            return False

    def restart_all(self, wait=True):
        try:
            self.stop_all(wait)
            self.start_all(wait)
            return True
        except Fault, e:
            print e
            return False

    def restart(self, name, wait=True):
        try:
            self.stop(name, wait)
            self.start(name, wait)
            return False
        except Fault:
            return False
