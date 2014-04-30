from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.conf import settings
import os
import json
import sys

from src.servers import Servers, Server

# Create your views here.


backend = Servers()
def monitor(request):
    backend.refresh()
    return render(
        request,
        'supervisor_monitor/templates/monitor.html',
        {
            'servers': backend.servers,
            'query_url': reverse('query'),
            'constants': {
                'stopped': 0,
                'running': 20,
                'fatal': 200,
            },
        }
    )


def query(request):
    sid = request.GET['server']
    server = Server(backend.servers[sid].connection_string, sid)
    action = request.GET['action']
    response_dict = {}
    if action == 'refresh':
        if server.refresh():
            response_dict['status'] = server.status.values()
            response_dict['status'].sort(key=lambda x: (x['group'], x['name']))
        else:
            response_dict['status'] = None

        response_dict['server'] = {'name': server.name, 'sid': sid}
        backend.servers[sid] = server

    elif action in ('start', 'stop', 'restart'):
        program = request.GET['program']
        getattr(server, action)(program)

    elif action in ('start_all', 'stop_all', 'restart_all'):
        try:
            getattr(server, action)()
        except:
            print "Unexpected error:", sys.exc_info()[0]

    return HttpResponse(json.dumps(response_dict), mimetype='application/javascript')
