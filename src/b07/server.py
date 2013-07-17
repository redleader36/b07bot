# -*- mode: python; coding: utf-8 -*-

# b07 bot - ingress information bot
# Copyright © 2013 b07@tormail.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from twisted.internet import reactor

from b07.log import setup
from b07.log import TRACE

# it's very important to set up logging very early in the life of an
# application...
setup(reactor, TRACE)

import os
import ConfigParser

from twisted.internet import endpoints
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web.util import Redirect

import txws
import json

from b07.log import trace, debug

import b07.api
import b07.portals

class WebSocketProtocol(Protocol):
    def dataReceived(self, data):
        trace('{}'.format(data))
        request = json.loads(data)
        if request['action'] == 'list':
            if request['what'] == 'portals':
                self.sendPortalList()

    def sendPortalList(self):
        debug('getting list of portals')
        portals = b07.portals.jsonlist()
        data = json.dumps(portals)
        debug('sending list of portals')
        self.transport.write(data)

class HttpsRedirect(Resource):
    def render_GET(self, request):
        request.setResponseCode(302)

def main():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.b07'))
    api = b07.api.API(reactor,
                      config.get('ingress', 'email'),
                      config.get('ingress', 'password'))
    

    http_root = Redirect('https://localhost:{}/'.format(config.get('server', 'https_port')))
    http_factory = Site(http_root)
    http_endpoint = endpoints.serverFromString(reactor,
                                               'tcp:{}'.format(config.get('server', 'http_port')))
    http_endpoint.listen(http_factory)

    https_root = File(os.path.expanduser(config.get('server', 'web_root')))
    https_root.indexNames = ['index.html']
    https_factory = Site(https_root)
    https_endpoint = endpoints.serverFromString(reactor,
                                                'ssl:{}:privateKey={}:certKey={}'.format(config.get('server', 'https_port'),
                                                                                         os.path.expanduser(config.get('server', 'ssl_key')),
                                                                                         os.path.expanduser(config.get('server', 'ssl_cert'))))
    https_endpoint.listen(https_factory)

    wsfactory = Factory()
    wsfactory.protocol = WebSocketProtocol
    wss_endpoint = endpoints.serverFromString(reactor,
                                              'ssl:{}:privateKey={}:certKey={}'.format(config.get('server', 'wss_port'),
                                                                                       os.path.expanduser(config.get('server', 'ssl_key')),
                                                                                       os.path.expanduser(config.get('server', 'ssl_cert'))))
    wss_endpoint.listen(txws.WebSocketFactory(wsfactory))



    reactor.run()

if __name__ == '__main__':
    main()
