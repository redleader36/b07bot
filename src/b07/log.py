# - mode: python; coding: utf-8 -*-

import sys

write = sys.stderr.write
flush = sys.stderr.flush

import time
import traceback

from twisted.python import log
from twisted.python import util

TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL = range(6)

class Observer(object):
    def __init__(self, reactor, level):
        global write
        global flush

        self.reactor = reactor
        self.level = level

        self.write = write
        self.flush = flush

    def emit(self, eventDict):
        if not eventDict.has_key('level'):
            if eventDict.has_key('isError') and eventDict['isError']:
                eventDict['level'] = ERROR

            else:
                eventDict['level'] = TRACE

        if eventDict['level'] < self.level:
            return

        text = log.textFromEventDict(eventDict)
        if text is None:
            return

        text = text.rstrip()
        text = text.expandtabs()
        text += '\n'
        text = text.encode('utf-8')

        util.untilConcludes(self.write, text)
        util.untilConcludes(self.flush)

__all__ = ['setup',
           'trace', 'debug', 'info', 'warning', 'error', 'critical',
           'TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

observer = None

def msg(*message, **kw):
    global write
    global flush

    if observer is None:
        write('logging is not set up yet!')
        flush()
        sys.exit(1)

    log.msg(*message, **kw)

def trace(*message, **kw):
    kw['level'] = TRACE
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def debug(*message, **kw):
    kw['level'] = DEBUG
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def info(*message, **kw):
    kw['level'] = INFO
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def warning(*message, **kw):
    kw['level'] = WARNING
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def error(*message, **kw):
    kw['level'] = ERROR
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def critical(*message, **kw):
    kw['level'] = CRITICAL
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def setup(reactor, level = DEBUG):
    global observer

    observer = Observer(reactor, level)
    
    log.startLoggingWithObserver(observer.emit, setStdout = 1)
