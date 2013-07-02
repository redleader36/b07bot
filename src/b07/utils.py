#! -*- mode: python; coding: utf-8 -*-

import json

from zope.interface import implements
from twisted.internet import defer
from twisted.web.iweb import IBodyProducer
from twisted.internet.protocol import Protocol

from b07.log import trace, debug

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)
        trace('length: {}'.format(self.length))

    def startProducing(self, consumer):
        consumer.write(self.body)
        trace('wrote body')
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

class LoginProtocol(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.buffer = ''

    def dataReceived(self, data):
        self.buffer += data

    def connectionLost(self, reason):
        trace('Finished receiving body: {}'.format(reason.getErrorMessage()))
        self.finished.callback(dict(x.split("=") for x in self.buffer.split("\n") if x))

class JsonProtocol(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.buffer = ''

    def dataReceived(self, data):
        self.buffer += data

    def connectionLost(self, reason):
        trace('Finished receiving body: {}'.format(reason.getErrorMessage()))
        self.finished.callback(json.loads(self.buffer.replace('while(1);', '')))
