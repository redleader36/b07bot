# -*- mode: python; coding: utf-8 -*-

import os
import ConfigParser

from twisted.internet import reactor

from b07.log import setup
from b07.log import INFO

setup(reactor, INFO)

import b07.api
import b07.portals

def logportals(inventory, reactor):
    b07.portals.logportals()
    reactor.stop()

def main():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.b07'))
    api = b07.api.API(reactor,
                      config.get('ingress', 'email'),
                      config.get('ingress', 'password'))
    api.onInventoryRefreshed(logportals, reactor)

    reactor.run()

if __name__ == '__main__':
    main()
